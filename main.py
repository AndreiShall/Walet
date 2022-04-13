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
    def __init__(self, dataDir="", mnemonic=None, key=None, walletName=None):
        self.dataDir = dataDir

        if not(os.path.exists(os.path.join(dataDir, "conf.cfg"))):
            self.saveConf({"appSettings": {"lang": "eng","theme": "white"},"walletSettings": {"defaultWallet": None,"defaultChain": "Ethereum","endWallet": 0}})

        with open(os.path.join(dataDir, "conf.cfg"), "r") as confFile:
            conf = json.load(confFile)
            provider = "https://data-seed-prebsc-1-s1.binance.org:8545"#providers["rpc_url"][conf["walletSettings"]["defaultChain"]]
            self.lang = conf["appSettings"]["lang"]
            self.theme = conf["appSettings"]["theme"]
            self.chain = conf["walletSettings"]["defaultChain"]

            if (mnemonic == None) and (key == None):
                if conf["walletSettings"]["defaultWallet"] == None:
                    conf["walletSettings"]["defaultWallet"] = os.path.join(dataDir, str("wallet" + str(conf["walletSettings"]["endWallet"])))
                    conf["walletSettings"]["endWallet"] += 1
                    self.newWallet(conf["walletSettings"]["defaultWallet"], provider)
                else:
                    self.importWallet(conf["walletSettings"]["defaultWallet"], provider)
            elif mnemonic == None:
                conf["walletSettings"]["defaultWallet"] = os.path.join(dataDir, str("wallet" + str(conf["walletSettings"]["endWallet"])))
                conf["walletSettings"]["endWallet"] += 1
                self.importWallet(conf["walletSettings"]["defaultWallet"], provider, key=key)
            else:
                conf["walletSettings"]["defaultWallet"] = os.path.join(dataDir, str("wallet" + str(conf["walletSettings"]["endWallet"])))
                conf["walletSettings"]["endWallet"] += 1
                self.importWallet(conf["walletSettings"]["defaultWallet"], provider, mnemonic=mnemonic)

            self.saveConf(conf)

            self.wallet = conf["walletSettings"]["defaultWallet"]

    def walletBalance(self):
        balance = {}
        for token in self.tokens:
            tokenBalance = self.crypto.balance(token)
            if tokenBalance[1] == None:
                balance[providers["coins"][self.chain]] = tokenBalance[0]
            else:
                balance[tokenBalance[1]] = tokenBalance[0]
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

    def sendTo(self, recipient, amount, token=None, gas = 21000, gasPrice = 50):
        self.crypto.send(recipient, amount, token, gas, gasPrice)

    def walletAddress(self):
        return self.crypto.address()

if __name__ == "__main__":
    wallet = WalletCore()

    print(wallet.walletBalance())
    wallet.sendTo("0x9aF3c7Bf0095Cb8273c2C19412BB4f5951f09987", 0.5, token="0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee")
    print(wallet.walletBalance())
