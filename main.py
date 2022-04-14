from kivy.lang import Builder
from kivy.properties import ObjectProperty

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.icon_definitions import md_icons

from kivymd.uix.card import MDCard

from kivymd.uix.behaviors import RoundedRectangularElevationBehavior

from kivymd.uix.list import OneLineListItem
from kivymd.uix.label import MDLabel
from kivy.clock import mainthread

import threading
from time import sleep

from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
from web3.middleware import geth_poa_middleware
import json, os

providers = {
    "rpc_url": {
        "Ethereum": "https://rpc.ankr.com/eth",
        "Binance Smart Chain": "https://bsc-dataseed.binance.org",
        "Polygon": "https://polygon-rpc.com",
        "Fantom": "https://rpc.fantom.network",
        "Solana": "https://solana.public-rpc.com"
    },

    "coins": {
        "Ethereum": "ETH",
        "Binance Smart Chain": "BNB",
        "Polygon": "MATIC",
        "Fantom": "FTM",
        "Solana": "SLN"
    }
}

class CryptoCore:
    def __init__(self, mnemonic = None, key = None, provider = ""):
        self.web3 = Web3(HTTPProvider(provider))
        self.web3.eth.account.enable_unaudited_hdwallet_features()
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.abi = [{'constant': True, 'inputs': [], 'name': 'name', 'outputs': [{'name': '', 'type': 'string'}], 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_from', 'type': 'address'}, {'name': '_to', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}], 'name': 'transferFrom', 'outputs': [{'name': 'success', 'type': 'bool'}], 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'decimals', 'outputs': [{'name': '', 'type': 'uint8'}], 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'name': '', 'type': 'uint256'}], 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'symbol', 'outputs': [{'name': '', 'type': 'string'}], 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_to', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}], 'name': 'transfer', 'outputs': [], 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_spender', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}, {'name': '_extraData', 'type': 'bytes'}], 'name': 'approveAndCall', 'outputs': [{'name': 'success', 'type': 'bool'}], 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'address'}, {'name': '', 'type': 'address'}], 'name': 'spentAllowance', 'outputs': [{'name': '', 'type': 'uint256'}], 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'address'}, {'name': '', 'type': 'address'}], 'name': 'allowance', 'outputs': [{'name': '', 'type': 'uint256'}], 'type': 'function'}, {'inputs': [{'name': 'initialSupply', 'type': 'uint256'}, {'name': 'tokenName', 'type': 'string'}, {'name': 'decimalUnits', 'type': 'uint8'}, {'name': 'tokenSymbol', 'type': 'string'}], 'type': 'constructor'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'from', 'type': 'address'}, {'indexed': True, 'name': 'to', 'type': 'address'}, {'indexed': False, 'name': 'value', 'type': 'uint256'}], 'name': 'Transfer', 'type': 'event'}]
        self.mnemonic = None
        if mnemonic == None:
            if key == None:
                self.account, self.mnemonic = self.web3.eth.account.create_with_mnemonic()
            else:
                self.account = self.web3.eth.account.from_key(key)
        else:
            self.account = self.web3.eth.account.from_mnemonic(mnemonic)

    def __del__(self):
        del self.web3
        del self.account
        del self.mnemonic

    def mnemonic(self):
        return self.mnemonic

    def key(self):
        return self.account.key

    def address(self):
        return self.account.address

    def balance(self, token=None):
        balance = -1
        if token == None:
            balance = (self.web3.fromWei(self.web3.eth.getBalance(self.account.address), "ether"), None)
        else:
            addr = self.web3.toChecksumAddress(token)
            contract = self.web3.eth.contract(abi=self.abi, address=addr)
            balance = (self.web3.fromWei(contract.caller.balanceOf(self.address()), "ether"), contract.caller.name())
        return balance

    def send(self, recipient, amount, token=None, gas = 21000, gasPrice = 50):
        if token == None:
            transaction = {
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
                "to": recipient,
                #"from": self.account.address,
                "value": self.web3.toWei(amount, "ether"),
                "gas": gas,
                "gasPrice": self.web3.toWei(gasPrice, "gwei")
            }
        else:
            addr = self.web3.toChecksumAddress(token)
            contract = self.web3.eth.contract(abi=self.abi, address=addr)
            transaction = contract.functions.transfer(self.web3.toChecksumAddress(recipient), self.web3.toWei(amount, "ether")).buildTransaction({
        #"value": self.web3.toWei(amount, "ether"),
        "nonce": self.web3.eth.get_transaction_count(self.account.address),
        "from": self.web3.toChecksumAddress(self.account.address),
        #"gas": gas,
        "gasPrice": self.web3.toWei(gasPrice, "gwei")
    })#.transact({"from": self.web3.toChecksumAddress(self.account.address)})

        sing_transaction = self.web3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = self.web3.eth.send_raw_transaction(sing_transaction.rawTransaction)
        self.web3.eth.wait_for_transaction_receipt(tx_hash)

class WalletCore:
    def __init__(self, dataDir=""):
        self.dataDir = dataDir

    def exists(self):
        if not(os.path.exists(os.path.join(self.dataDir, "conf.cfg"))):
            self.saveConf({"appSettings": {"lang": "eng","theme": "white"},"walletSettings": {"defaultWallet": None,"defaultChain": "Ethereum","endWallet": 0}})

        with open(os.path.join(self.dataDir, "conf.cfg"), "r") as confFile:
            conf = json.load(confFile)
            provider = "https://data-seed-prebsc-1-s1.binance.org:8545"#providers["rpc_url"][conf["walletSettings"]["defaultChain"]]
            self.lang = conf["appSettings"]["lang"]
            self.theme = conf["appSettings"]["theme"]
            self.chain = conf["walletSettings"]["defaultChain"]

            if conf["walletSettings"]["defaultWallet"] != None:
                self.importWallet(conf["walletSettings"]["defaultWallet"], provider)
                return "OK"

            conf["walletSettings"]["defaultWallet"] = os.path.join(self.dataDir, str("wallet" + str(conf["walletSettings"]["endWallet"])))
            conf["walletSettings"]["endWallet"] += 1

            self.saveConf(conf)

            self.wallet = conf["walletSettings"]["defaultWallet"]

            return (self.wallet, provider)

    def __del__(self):
        del self.crypto

    def walletBalance(self):
        self.tokenss= []
        balance = {}
        for token in self.tokens:
            tokenBalance = self.crypto.balance(token)
            if tokenBalance[1] == None:
                balance[providers["coins"][self.chain]] = tokenBalance[0]
                self.tokenss.append((providers["coins"][self.chain], None))
            else:
                balance[tokenBalance[1]] = tokenBalance[0]
                self.tokenss.append((tokenBalance[1], token))
        return balance

    def newWallet(self, walletName, provider):
        self.crypto = CryptoCore(provider = provider)
        self.tokens = [None]
        self.saveWallet(walletName, {"tokens": []}, self.crypto.key())

    def importWallet(self, walletName, provider, key=None, mnemonic=None):
        if (mnemonic == None) and (key == None):
            with open(walletName + ".cfg", "r") as walletFile:
                walletConf = json.load(walletFile)
                self.tokens = [None]
                for token in walletConf["tokens"]:
                    if token[1] == self.chain:
                        self.tokens.append(token[0])
            with open(walletName + ".key", "rb") as keyFile:
                self.crypto = CryptoCore(key = keyFile.read(), provider = provider)
        else:
            if mnemonic == None:
                self.crypto = CryptoCore(key = key, provider = provider)
            else:
                self.crypto = CryptoCore(mnemonic = mnemonic, provider = provider)

            self.tokens = [None]
            self.saveWallet(walletName, {"tokens": []}, self.crypto.key())

    def saveConf(self, conf):
        with open(os.path.join(self.dataDir, "conf.cfg"), "w") as confFile:
            json.dump(conf, confFile)

    def saveWallet(self, walletName, walletConf, key):
        with open(walletName + ".cfg", "w") as walletFile:
            json.dump(walletConf, walletFile)
        with open(walletName + ".key", "wb") as keyFile:
            keyFile.write(key)

    def addToken(self, tokenAddress):
        with open(self.wallet + ".cfg", "r") as walletFile:
            walletConf = json.load(walletFile)
            walletConf["tokens"].append((tokenAddress, self.chain))
            with open(self.wallet + ".cfg", "w") as walletFile:
                json.dump(walletConf, walletFile)

    def sendTo(self, recipient, amount, coin=None, gas = 21000, gasPrice = 50):
        for token in self.tokenss:
            if token[0] == coin:
                self.crypto.send(recipient, amount, token[1], gas, gasPrice)

    def walletAddress(self):
        return self.crypto.address()

KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<ContentNavigationDrawer>

    ScrollView:

        MDList:

            OneLineIconListItem:
                text: "Wallet"
                on_press:
                    root.nav_drawer.set_state("close")
                    root.screen_manager.current = "wallet_screen"
                IconLeftWidget:
                    icon: "bitcoin"

<MD3Card>
    padding: 16

    MDRelativeLayout:
        size_hint: None, None
        size: root.size

        MDIconButton:
            icon: "dots-vertical"
            pos:
                root.width - (self.width + root.padding[0] + dp(4)), root.height - (self.height + root.padding[0] + dp(4))

        ScrollView:
            pos_hint: {"top": .88, "right": .9}
            size_hint: .9, .8
            MDList:
                id: balance

        MDLabel:
            id: label
            text: root.text
            adaptive_size: True
            color: .2, .2, .2, .8

MDScreen:

    MDToolbar:
        id: toolbar
        pos_hint: {"top": 1}
        elevation: 10
        size_hint: 1, .1
        title: "Walet"
        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]

    MDNavigationLayout:
        x: toolbar.height

        ScreenManager:
            id: screen_manager

            MDScreen:
                name: "wallet_screen"

                MD3Card:
                    pos_hint: {"top": .875, "right": .975}
                    text: "wallet"
                    style: "filled"
                    md_bg_color: get_color_from_hex("#f4dedc")
                    radius: self.height / 10
                    size_hint: .95, .475
                    id: card

                MDFillRoundFlatIconButton:
                    size_hint: .4, .1
                    pos_hint: {"top": .35, "right": .45}
                    icon: "cube-send"
                    text: "Send"
                    on_press:
                        screen_manager.current = "send_screen"

                MDFillRoundFlatIconButton:
                    size_hint: .4, .1
                    pos_hint: {"top": .35, "right": .95}
                    icon: "cube-scan"
                    text: "Get"
                    on_press:
                        screen_manager.current = "get_screen"

            MDScreen:
                name: "send_screen"

                MDLabel:
                    id: send_label

                MDTextField:
                    id: recipient_field
                    hint_text: "recipient address"
                    size_hint: .4, .1
                    pos_hint: {"top": .5, "right": .45}

                MDTextField:
                    id: amount_field
                    hint_text: "amount of tokens"
                    size_hint: .4, .1
                    pos_hint: {"top": .5, "right": .95}

                MDFillRoundFlatIconButton:
                    pos_hint: {"top": .35, "right": .45}
                    icon: "cube-send"
                    text: "Send"
                    on_press:
                        app.sendButtonClick(recipient_field.text, amount_field.text, app.currentToken)
                        amount_field.text = ""
                        recipient_field.text = ""
                        screen_manager.current = "wallet_screen"

                MDFillRoundFlatIconButton:
                    pos_hint: {"top": .35, "right": .95}
                    icon: "cube-off-outline"
                    text: "Cancel"
                    on_press:
                        amount_field.text = ""
                        recipient_field.text = ""
                        screen_manager.current = "wallet_screen"

            MDScreen:
                name: "get_screen"

                MDLabel:
                    id: address_label
                    text: "Address"
                    halign: "center"

            MDScreen:
                name: "reg_screen"

                MDTextField:
                    id: mnemonic_field
                    hint_text: "mnemonic"
                    size_hint: .4, .1
                    pos_hint: {"top": .5, "right": .95}

                MDFillRoundFlatIconButton:
                    pos_hint: {"top": .35, "right": .45}
                    icon: "cube-send"
                    text: "Import wallet"
                    on_press:
                        app.reg(mnemonic_field.text)
                        mnemonic_field.text = ""
                        screen_manager.current = "wallet_screen"

                MDFillRoundFlatIconButton:
                    pos_hint: {"top": .35, "right": .7}
                    icon: "cube-send"
                    text: "New wallet"
                    on_press:
                        app.newWallet()
                        mnemonic_key_field.text = ""
                        screen_manager.current = "wallet_screen"

        MDNavigationDrawer:
            id: nav_drawer

            ContentNavigationDrawer:
                screen_manager: screen_manager
                nav_drawer: nav_drawer
'''

class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    text = StringProperty()

class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

class Walet(MDApp):
    def build(self):
        self.wallet = WalletCore()
        self.theme_cls.primary_palette = "Indigo"
        return Builder.load_string(KV)

    def on_start(self):
        a = self.wallet.exists()
        if a != "OK":
            self.root.ids.screen_manager.current = "reg_screen"
            self.provider = a[1]
            self.walletName = a[0]
        else:
            self.gg = True
            self.balance_thread = threading.Thread(target=self.updateBalance, args=())
            self.balance_thread.start()
            address = self.wallet.walletAddress()
            self.root.ids.address_label.text = address

    def on_stop(self):
        self.gg = False
        #self.balance_thread.join()
        del self.wallet

    def sendButtonClick(self, recipient, amount, token):
        self.wallet.sendTo(recipient, amount, token)

    def openCoinScreen(self, coin):
        self.currentToken = coin
        self.root.ids.send_label.text = "You send: " + coin
        self.root.ids.screen_manager.current = "send_screen"

    def updateBalance(self):
        while self.gg:
            balance = self.wallet.walletBalance()
            self.printBalance(balance)
            for i in range(60):
                if not(self.gg):
                    break
                sleep(1)

    def reg(self, inp):
        try:
            inp.split()
            self.wallet.importWallet(self.walletName, self.provider, mnemonic = inp)
        except:
            self.wallet.importWallet(self.walletName, self.provider, key = inp)
        self.gg = True
        self.balance_thread = threading.Thread(target=self.updateBalance, args=())
        self.balance_thread.start()
        address = self.wallet.walletAddress()
        self.root.ids.address_label.text = address

    def newWallet(self):
        self.wallet.newWallet(self.walletName, self.provider)
        self.gg = True
        self.balance_thread = threading.Thread(target=self.updateBalance, args=())
        self.balance_thread.start()
        address = self.wallet.walletAddress()
        self.root.ids.address_label.text = address

    @mainthread
    def printBalance(self, balance):
        self.root.ids.card.ids.balance.clear_widgets()
        for coin in balance:
            self.root.ids.card.ids.balance.add_widget(OneLineListItem(text=f"{coin}: {balance[coin]}", on_press=lambda x: self.openCoinScreen(x.text.split(":")[0])))

Walet().run()
