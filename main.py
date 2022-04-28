from kivy.lang import Builder

from kivymd.app import MDApp

from kivymd.uix.list import OneLineListItem
from kivy.clock import mainthread
from kivymd.uix.list import MDList
import platform

import threading
from time import sleep

from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
from web3.middleware import geth_poa_middleware

from kivy.core.clipboard import Clipboard
from kivymd.uix.menu import MDDropdownMenu

import json, os, requests

if platform.system() == "Linux":
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
    from Crypto.Cipher import AES, PKCS1_OAEP
else:
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Random import get_random_bytes
    from Cryptodome.Cipher import AES, PKCS1_OAEP

from base64 import b64encode, b64decode

from os.path import join

KV = """
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import Clipboard kivy.core.clipboard.Clipboard
#:import Svg kivy.graphics.svg

MDScreen:

    ScreenManager:
        id: mainScrMan

        MDScreen:
            name: "main"

            MDBottomNavigation:
                panel_color: get_color_from_hex("#eeeaea")
                selected_color_background: get_color_from_hex("#97ecf8")
                text_color_active: 0, 0, 0, 1

                MDBottomNavigationItem:
                    name: "screen 1"
                    text: "Портфолио"
                    icon: "briefcase"
                    badge_icon: "numeric-10"

                    MDScreen:
                        name: "wallet"

                        BoxLayout:
                            size_hint_y: .4
                            pos_hint: {"center_x": .5, "center_y": .8}

                            canvas:
                                Color:
                                    rgba: get_color_from_hex("#ff5733")
                                Rectangle:
                                    pos: self.pos
                                    size: self.size

                            MDLabel:
                                id: balanceDollarView
                                color: get_color_from_hex("#f5e8e5")
                                font_style: "H3"
                                halign: "center"

                        ScrollView:
                            pos_hint: {"center_x": .5, "center_y": .1}
                            size_hint_y: 1

                            MDList:
                                id: coinsView

                MDBottomNavigationItem:
                    name: "screen 3"
                    text: "Настройки"
                    icon: "cog"

                    ScrollView:

                        MDList:
                            canvas:
                                Color:
                                    rgba: get_color_from_hex("#eeeaea")
                                Rectangle:
                                    pos: self.pos
                                    size: self.size

                            OneLineListItem:
                                text: "Добавить токен"
                                on_press:
                                    app.updateDropMenu()
                                    mainScrMan.current = "settings"
                                    setScrMan.current = "addToken"

                            OneLineListItem:
                                text: "Сменить кошелек"
                                on_press:
                                    mainScrMan.current = "settings"
                                    setScrMan.current = "changeWallet"

                            OneLineListItem:
                                text: "Добавить сеть"
                                on_press:
                                    mainScrMan.current = "settings"
                                    setScrMan.current = "addChain"


        MDScreen:
            name: "coin"

            BoxLayout:
                size_hint_y: .4
                pos_hint: {"center_x": .5, "center_y": .8}

                canvas:
                    Color:
                        rgba: get_color_from_hex("#ff5733")
                    Rectangle:
                        pos: self.pos
                        size: self.size

                MDLabel:
                    id: balanceCoinView
                    color: get_color_from_hex("#f5e8e5")
                    font_style: "H3"
                    halign: "center"
                    pos_hint: {"center_x": .5, "center_y": .65}

            MDFillRoundFlatIconButton:
                text_color: get_color_from_hex("#ff5733")
                icon_color: get_color_from_hex("#ff5733")
                md_bg_color: get_color_from_hex("#f5e8e5")
                icon: "android"
                text: "Скопировать адрес кошелька"
                pos_hint: {"center_x": .5, "center_y": .75}
                on_press:
                    app.copyAddr()

            MDLabel:
                text: "Отправить криптовалюту"
                color: get_color_from_hex("#ff5733")
                font_style: "H5"
                halign: "center"
                pos_hint: {"center_x": .5, "center_y": .55}

            MDTextField:
                id: amountField
                hint_text: "Сумма перевода"
                text_color: get_color_from_hex("#ff5733")
                current_hint_text_color: get_color_from_hex("#ff5733")
                size_hint: .9, .1
                line_color_focus: get_color_from_hex("#f5e8e5")
                mode: "rectangle"
                pos_hint: {"center_x": .5, "center_y": .45}

            MDTextField:
                id: recipientField
                hint_text: "Адрес получателя"
                text_color: get_color_from_hex("#ff5733")
                current_hint_text_color: get_color_from_hex("#ff5733")
                size_hint: .9, .1
                line_color_focus: get_color_from_hex("#f5e8e5")
                mode: "rectangle"
                pos_hint: {"center_x": .5, "center_y": .35}

            MDTextField:
                id: sendPasswordField
                hint_text: "Введите пароль"
                text_color: get_color_from_hex("#ff5733")
                current_hint_text_color: get_color_from_hex("#ff5733")
                size_hint: .9, .1
                line_color_focus: get_color_from_hex("#f5e8e5")
                mode: "rectangle"
                pos_hint: {"center_x": .5, "center_y": .25}

            MDFillRoundFlatIconButton:
                text_color: get_color_from_hex("#f5e8e5")
                icon_color: get_color_from_hex("#f5e8e5")
                md_bg_color: get_color_from_hex("#ff5733")
                icon: "android"
                text: "Отправить"
                pos_hint: {"center_x": .5, "center_y": .15}
                on_press:
                    app.sendTokens(recipientField.text, amountField.text, sendPasswordField.text)
                    sendPasswordField.text = ""
                    recipientField.text = ""
                    amountField.text = ""

            MDFillRoundFlatIconButton:
                text_color: get_color_from_hex("#f5e8e5")
                icon_color: get_color_from_hex("#f5e8e5")
                md_bg_color: get_color_from_hex("#ff5733")
                icon: "android"
                text: "Назад"
                pos_hint: {"center_x": .5, "center_y": .05}
                on_press:
                    mainScrMan.current = "main"
                    sendPasswordField.text = ""
                    recipientField.text = ""
                    amountField.text = ""

        MDScreen:
            name: "createWallet"

            ScreenManager:
                id: createWalletScrMan

                MDScreen:
                    name: "walletHave"
                    MDLabel:
                        color: get_color_from_hex("#ff5733")
                        font_style: "H5"
                        text: "У вас есть кошелек?"
                        halign: "center"
                        pos_hint: {"center_x": .5, "center_y": .55}

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Да, я хочу импортировать кошелек"
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_press:
                            createWalletScrMan.current = "importWallet"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Нет, я хочу создать новый кошелек"
                        pos_hint: {"center_x": .5, "center_y": .35}
                        on_press:
                            app.getNewMnemonic()
                            createWalletScrMan.current = "newWallet"

                MDScreen:
                    name: "importWallet"

                    MDTextField:
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        id: mnemonicField
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .75}
                        hint_text: "Мнемоническая фраза"

                    MDTextField:
                        id: walletNameField
                        hint_text: "Имя кошелька"
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .65}

                    MDTextField:
                        id: createPasswordField
                        hint_text: "Создать пароль"
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .55}

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Импортировать кошелек"
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_press:
                            app.importWallet(mnemonicField.text, createPasswordField.text, walletNameField.text)
                            mainScrMan.current = "enterPassword"
                            mnemonicField.text = ""
                            createPasswordField.text = ""
                            walletNameField.text = ""

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .35}
                        on_press:
                            createWalletScrMan.current = "walletHave"
                            mnemonicField.text = ""
                            createPasswordField.text = ""
                            walletNameField.text = ""

                MDScreen:
                    name: "newWallet"

                    MDLabel:
                        text: "Ваша мнемоническая фраза:"
                        halign: "center"
                        color: get_color_from_hex("#ff5733")
                        font_style: "H5"
                        pos_hint: {"center_x": .5, "center_y": .65}

                    MDLabel:
                        id: mnemonicLabel
                        halign: "center"
                        color: get_color_from_hex("#ff5733")
                        pos_hint: {"center_x": .5, "center_y": .6}

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Копировать"
                        pos_hint: {"center_x": .5, "center_y": .4}
                        on_press:
                            Clipboard.put(mnemonicLabel.text)
                            createWalletScrMan.current = "importWallet"
                            mnemonicLabel.text = ""

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .3}
                        on_press:
                            createWalletScrMan.current = "walletHave"
                            mnemonicLabel.text = ""

        MDScreen:
            name: "enterPassword"

            MDTextField:
                id: passwordField
                hint_text: "Введите пароль"
                text_color: get_color_from_hex("#ff5733")
                current_hint_text_color: get_color_from_hex("#ff5733")
                size_hint: .9, .1
                line_color_focus: get_color_from_hex("#f5e8e5")
                mode: "rectangle"
                pos_hint: {"center_x": .5, "center_y": .55}

            MDFillRoundFlatIconButton:
                text_color: get_color_from_hex("#f5e8e5")
                icon_color: get_color_from_hex("#f5e8e5")
                md_bg_color: get_color_from_hex("#ff5733")
                icon: "android"
                text: "Готово"
                pos_hint: {"center_x": .5, "center_y": .45}
                on_press:
                    app.openWallet(passwordField.text)
                    passwordField.text = ""
                    mainScrMan.current = "main"

        MDScreen:
            name: "settings"

            ScreenManager:
                id: setScrMan

                MDScreen:
                    name: "addChain"

                    MDTextField:
                        id: chainNameField
                        hint_text: "Главный токен сети"
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .75}

                    MDTextField:
                        id: rpcurlField
                        hint_text: "RPC_URL сети"
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .65}

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Готово"
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_press:
                            app.addChain(chainNameField.text, rpcurlField.text)
                            chainNameField.text = ""
                            rpcurlField.text = ""
                            mainScrMan.current = "main"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .3}
                        on_press:
                            chainNameField.text = ""
                            rpcurlField.text = ""
                            mainScrMan.current = "main"

                MDScreen:
                    name: "importNewWallet"

                    MDTextField:
                        id: newMnemonicField
                        hint_text: "Мнемоническая фраза"
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .75}

                    MDTextField:
                        id: newWalletNameField
                        hint_text: "Имя кошелька"
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .65}

                    MDTextField:
                        id: importPasswordField
                        hint_text: "Пароль"
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .55}

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Импортировать"
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_press:
                            app.importNewWallet(newMnemonicField.text, importPasswordField.text, newWalletNameField.text)
                            newMnemonicField.text = ""
                            newWalletNameField.text = ""
                            importPasswordField.text = ""
                            mainScrMan.current = "main"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .3}
                        on_press:
                            newMnemonicField.text = ""
                            newWalletNameField.text = ""
                            importPasswordField.text = ""
                            mainScrMan.current = "main"

                MDScreen:
                    name: "newWallet"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Импортировать кошелек"
                        pos_hint: {"center_x": .5, "center_y": .65}
                        on_press:
                            setScrMan.current = "importNewWallet"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Создать кошелек"
                        pos_hint: {"center_x": .5, "center_y": .55}
                        on_press:
                            app.getNewMnemonic2()
                            setScrMan.current = "createNewWallet"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_press:
                            mainScrMan.current = "main"

                MDScreen:
                    name: "createNewWallet"

                    MDLabel:
                        text: "Ваша мнемоническая фраза:"
                        halign: "center"
                        color: get_color_from_hex("#ff5733")
                        font_style: "H5"
                        pos_hint: {"center_x": .5, "center_y": .65}

                    MDLabel:
                        id: mnemonicLabel2
                        halign: "center"
                        color: get_color_from_hex("#ff5733")
                        pos_hint: {"center_x": .5, "center_y": .6}

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Копировать"
                        pos_hint: {"center_x": .5, "center_y": .4}
                        on_press:
                            Clipboard.put(mnemonicLabel2.text)
                            setScrMan.current = "importNewWallet"
                            mnemonicLabel2.text = ""

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .3}
                        on_press:
                            mainScrMan.current = "main"
                            mnemonicLabel2.text = ""

                MDScreen:
                    name: "changeWallet"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Сменить кошелек"
                        pos_hint: {"center_x": .5, "center_y": .65}
                        on_press:
                            app.updateChangeList()
                            setScrMan.current = "change"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Новый кошелек"
                        pos_hint: {"center_x": .5, "center_y": .55}
                        on_press:
                            setScrMan.current = "newWallet"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_press:
                            mainScrMan.current = "main"

                MDScreen:
                    name: "change"

                    ScrollView:
                        id: scroll

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_press:
                            mainScrMan.current = "main"

                MDScreen:
                    name: "addToken"

                    MDTextField:
                        id: tokenAddrField
                        hint_text: "Адрес токена"
                        text_color: get_color_from_hex("#ff5733")
                        current_hint_text_color: get_color_from_hex("#ff5733")
                        size_hint: .9, .1
                        line_color_focus: get_color_from_hex("#f5e8e5")
                        mode: "rectangle"
                        pos_hint: {"center_x": .5, "center_y": .7}

                    MDDropDownItem:
                        id: dropMenu
                        text: "Выберите сеть"
                        pos_hint: {"center_x": .5, "center_y": .6}
                        on_release: app.menu.open()

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Готово"
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_press:
                            app.addToken(tokenAddrField.text, dropMenu.current_item)
                            tokenAddrField.text = ""
                            mainScrMan.current = "main"

                    MDFillRoundFlatIconButton:
                        text_color: get_color_from_hex("#f5e8e5")
                        icon_color: get_color_from_hex("#f5e8e5")
                        md_bg_color: get_color_from_hex("#ff5733")
                        icon: "android"
                        text: "Назад"
                        pos_hint: {"center_x": .5, "center_y": .3}
                        on_press:
                            tokenAddrField.text = ""
                            mainScrMan.current = "main"
"""

class Cryptography:
    def __init__(self, dataDir):
        self.dataDir = dataDir

    def generateKey(self, code):
        key = RSA.generate(2048)
        self.privateKeyRSA = key.exportKey(passphrase=code, pkcs=8, protection="scryptAndAES128-CBC")
        self.publicKeyRSA = key.publickey()

    def exportKeys(self):
        with open(join(self.dataDir, "privateKey.bin"), "wb") as f:
            f.write(self.privateKeyRSA)

        with open(join(self.dataDir, "publicKey.pem"), "wb") as f:
            f.write(self.publicKeyRSA.exportKey())

    def importKeys(self, code):
        self.privateKeyRSA = RSA.import_key(open(join(self.dataDir, "privateKey.bin")).read(), passphrase=code)
        self.publicKeyRSA = RSA.import_key(open(join(self.dataDir, "publicKey.pem")).read())

    def encrypt(self, data):
        session_key = get_random_bytes(16)
        try:
            cipher_rsa = PKCS1_OAEP.new(RSA.import_key(self.publicKeyRSA.replace("\\n", "\n")))
        except:
            cipher_rsa = PKCS1_OAEP.new(self.publicKeyRSA)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(str(data).encode("utf8"))
        data = cipher_rsa.encrypt(session_key) + cipher_aes.nonce + tag + ciphertext
        return b64encode(data)

    def decrypt(self, data):
        enc_session_key, nonce, tag, ciphertext = (b64decode(data)[:self.privateKeyRSA.size_in_bytes()],
                                                   b64decode(data)[
                                                   self.privateKeyRSA.size_in_bytes():self.privateKeyRSA.size_in_bytes() + 16],
                                                   b64decode(data)[
                                                   self.privateKeyRSA.size_in_bytes() + 16:self.privateKeyRSA.size_in_bytes() + 32],
                                                   b64decode(data)[self.privateKeyRSA.size_in_bytes() + 32:])
        cipher_rsa = PKCS1_OAEP.new(self.privateKeyRSA)
        session_key = cipher_rsa.decrypt(enc_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return data.decode("utf8")

    def getKey(self):
        try:
            return str(self.publicKeyRSA.export_key("PEM"))[2:-1]
        except:
            return str(self.publicKeyRSA)[2:-1]

class CryptoCore:
    def __init__(self, mnemonic = None, key = None, provider = ""):
        self.web3 = Web3(HTTPProvider(provider))
        self.web3.eth.account.enable_unaudited_hdwallet_features()
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.abi = [{"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"}, {"constant": False, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "success", "type": "bool"}], "type": "function"}, {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}, {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}, {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"}, {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [], "type": "function"}, {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}, {"name": "_extraData", "type": "bytes"}], "name": "approveAndCall", "outputs": [{"name": "success", "type": "bool"}], "type": "function"}, {"constant": True, "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}], "name": "spentAllowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}, {"constant": True, "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}, {"inputs": [{"name": "initialSupply", "type": "uint256"}, {"name": "tokenName", "type": "string"}, {"name": "decimalUnits", "type": "uint8"}, {"name": "tokenSymbol", "type": "string"}], "type": "constructor"}, {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"}, {"indexed": True, "name": "to", "type": "address"}, {"indexed": False, "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"}]
        self.mnemonic = mnemonic
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
                "value": self.web3.toWei(amount, "ether"),
                "gas": gas,
                "gasPrice": self.web3.toWei(gasPrice, "gwei")
            }
        else:
            addr = self.web3.toChecksumAddress(token)
            contract = self.web3.eth.contract(abi=self.abi, address=addr)
            transaction = contract.functions.transfer(self.web3.toChecksumAddress(recipient), self.web3.toWei(amount, "ether")).buildTransaction({
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
                "from": self.web3.toChecksumAddress(self.account.address),
                "gasPrice": self.web3.toWei(gasPrice, "gwei")
            })

        sing_transaction = self.web3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = self.web3.eth.send_raw_transaction(sing_transaction.rawTransaction)
        self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def getTokenName(self, addr):
        contract = self.web3.eth.contract(abi=self.abi, address=self.web3.toChecksumAddress(addr))
        return contract.caller.name()

class WalletCore:
    def __init__(self, dataDir=""):
        self.dataDir = dataDir

    def exists(self):
        if not(os.path.exists(os.path.join(self.dataDir, "conf.cfg"))):
            self.saveConf({"defaultWallet": None, "walletsList": []})

        with open(os.path.join(self.dataDir, "conf.cfg"), "r") as confFile:
            conf = json.load(confFile)

            if conf["defaultWallet"] != None:
                self.wallet = conf["defaultWallet"]
                self.saveConf(conf)
                return False

            self.saveConf(conf)

        return True

    def changeWallet(self, walletName):
        with open(os.path.join(self.dataDir, "conf.cfg"), "r") as confFile:
            conf = json.load(confFile)
            conf["defaultWallet"] = walletName
            self.wallet = walletName
            self.saveConf(conf)
            self.importWalletFile()

    def getWalletList(self):
        with open(os.path.join(self.dataDir, "conf.cfg"), "r") as confFile:
            conf = json.load(confFile)
            return conf["walletsList"]

    def walletBalance(self, password):
        balance = {}
        with open(self.wallet + ".key", "rb") as keyFile:
            cryptography = Cryptography(self.dataDir)
            cryptography.importKeys(password)
            key = cryptography.decrypt(keyFile.read())
            for chain in self.providers:
                crypto = CryptoCore(mnemonic = key, provider = self.providers[chain])
                tokenBalance = crypto.balance(None)
                balance[chain] = tokenBalance[0]
            for token in self.tokens:
                crypto = CryptoCore(mnemonic = key, provider = self.providers[self.tokens[token]])
                tokenBalance = crypto.balance(token)
                balance[tokenBalance[1]] = tokenBalance[0]
        return balance

    def newWallet(self):
        crypto = CryptoCore(provider = "https://rpc.ankr.com/eth")
        return crypto.mnemonic

    def importWalletFile(self):
        with open(self.wallet + ".cfg", "r") as walletFile:
            walletConf = json.load(walletFile)
            self.tokens = {}
            for token in walletConf["tokens"]:
                self.tokens[token] = walletConf["tokens"][token]
            self.tokensAddr = {}
            for token in walletConf["tokensAddr"]:
                self.tokensAddr[token] = walletConf["tokensAddr"][token]
            self.providers = {
                "ETH": "https://rpc.ankr.com/eth",
                "BNB": "https://bsc-dataseed.binance.org",
                "MATIC": "https://polygon-rpc.com",
                "FTM": "https://rpc.ftm.tools"
            }
            for provider in walletConf["providers"]:
                self.providers[provider] = walletConf["providers"][provider]

    def importWallet(self, walletName, mnemonic, password):
        self.crypto = CryptoCore(mnemonic = mnemonic, provider = "https://rpc.ankr.com/eth")
        self.tokens = {}
        self.providers = {
            "ETH": "https://rpc.ankr.com/eth",
            "BNB": "https://bsc-dataseed.binance.org",
            "MATIC": "https://polygon-rpc.com",
            "FTM": "https://rpc.ftm.tools"
        }
        with open(os.path.join(self.dataDir, "conf.cfg"), "r") as confFile:
            conf = json.load(confFile)
            conf["defaultWallet"] = walletName
            self.wallet = walletName
            self.saveConf(conf)
        self.addWallet(walletName)
        self.saveWallet(walletName, {"tokens": {}, "tokensAddr": {}, "providers": {}}, self.crypto.mnemonic, password)

    def importNewWallet(self, walletName, mnemonic, password):
        self.crypto = CryptoCore(mnemonic = mnemonic, provider = "https://rpc.ankr.com/eth")
        self.tokens = {}
        self.providers = {
            "ETH": "https://rpc.ankr.com/eth",
            "BNB": "https://bsc-dataseed.binance.org",
            "MATIC": "https://polygon-rpc.com",
            "FTM": "https://rpc.ftm.tools"
        }
        with open(os.path.join(self.dataDir, "conf.cfg"), "r") as confFile:
            conf = json.load(confFile)
            conf["defaultWallet"] = walletName
            self.wallet = walletName
            self.saveConf(conf)
        self.addWallet(walletName)
        self.saveNewWallet(walletName, {"tokens": {}, "tokensAddr": {}, "providers": {}}, self.crypto.mnemonic, password)

    def saveConf(self, conf):
        with open(os.path.join(self.dataDir, "conf.cfg"), "w") as confFile:
            json.dump(conf, confFile)

    def saveWallet(self, walletName, walletConf, key, password, onlyConf=False):
        with open(walletName + ".cfg", "w") as walletFile:
            json.dump(walletConf, walletFile)
        if not(onlyConf):
            with open(walletName + ".key", "wb") as keyFile:
                cryptography = Cryptography(self.dataDir)
                cryptography.generateKey(password)
                cryptography.exportKeys()
                key = cryptography.encrypt(key)
                keyFile.write(key)

    def saveNewWallet(self, walletName, walletConf, key, password, onlyConf=False):
        with open(walletName + ".cfg", "w") as walletFile:
            json.dump(walletConf, walletFile)
        if not(onlyConf):
            with open(walletName + ".key", "wb") as keyFile:
                cryptography = Cryptography(self.dataDir)
                cryptography.importKeys(password)
                key = cryptography.encrypt(key)
                keyFile.write(key)

    def addToken(self, tokenAddress, tokenChain):
        with open(self.wallet + ".cfg", "r") as walletFile:
            crypto = CryptoCore(provider = self.providers[tokenChain])
            walletConf = json.load(walletFile)
            walletConf["tokens"][tokenAddress] = tokenChain
            walletConf["tokensAddr"][crypto.getTokenName(tokenAddress)] = tokenAddress
            with open(self.wallet + ".cfg", "w") as walletFile:
                json.dump(walletConf, walletFile)

        with open(self.wallet + ".cfg", "r") as walletFile:
            walletConf = json.load(walletFile)
            self.tokens = {}
            for token in walletConf["tokens"]:
                self.tokens[token] = walletConf["tokens"][token]
            self.tokensAddr = {}
            for token in walletConf["tokensAddr"]:
                self.tokensAddr[token] = walletConf["tokensAddr"][token]

    def addProvider(self, providerCoin, providerRPC_URL):
        with open(self.wallet + ".cfg", "r") as walletFile:
            walletConf = json.load(walletFile)
            walletConf["providers"][providerCoin] = providerRPC_URL
            with open(self.wallet + ".cfg", "w") as walletFile:
                json.dump(walletConf, walletFile)

        self.providers = {
            "ETH": "https://rpc.ankr.com/eth",
            "BNB": "https://bsc-dataseed.binance.org",
            "MATIC": "https://polygon-rpc.com",
            "FTM": "https://rpc.ftm.tools",
            "BnB": "https://data-seed-prebsc-1-s1.binance.org:8545"
        }
        for provider in walletConf["providers"]:
            self.providers[provider] = walletConf["providers"][provider]


    def sendTo(self, recipient, amount, password, coin, gas = 21000, gasPrice = 50):
        with open(self.wallet + ".key", "rb") as keyFile:
            cryptography = cryptography(self.dataDir)
            cryptography.importKeys(password)
            key = cryptography.decrypt(keyFile.read())
            crypto = CryptoCore(mnemonic = key, provider = self.providers[coin])
            crypto.send(recipient, amount, None, gas, gasPrice)

    def sendToken(self, recipient, amount, password, coin, gas = 21000, gasPrice = 50):
        with open(self.wallet + ".key", "rb") as keyFile:
            cryptography = cryptography(self.dataDir)
            cryptography.importKeys(password)
            key = cryptography.decrypt(keyFile.read())
            crypto = CryptoCore(mnemonic = key, provider = self.providers[self.tokens[self.tokensAddr[coin]]])
            crypto.send(recipient, amount, self.tokensAddr[coin], gas, gasPrice)

    def walletAddress(self, password):
        with open(self.wallet + ".key", "rb") as keyFile:
            cryptography = Cryptography(self.dataDir)
            cryptography.importKeys(password)
            key = cryptography.decrypt(keyFile.read())
            crypto = CryptoCore(mnemonic = key, provider = "https://rpc.ankr.com/eth")
            return crypto.address()

    def addWallet(self, walletName):
        with open(os.path.join(self.dataDir, "conf.cfg"), "r") as confFile:
            conf = json.load(confFile)
            conf["walletsList"].append(walletName)
            self.saveConf(conf)

    def balanceInUSD(self, balance):
        usdBalance = 0
        for coin in balance:
            key = "https://api.binance.com/api/v3/ticker/price?symbol=" + coin + "USDT"
            try:
                price = float(json.loads(requests.get(key).text)["price"])
                usdBalance += float(balance[coin])*price
            except:
                pass
        return round(usdBalance, 2)

class Walet(MDApp):

    def build(self):
        self.theme_cls.material_style = "M3"
        self.wallet = WalletCore()
        return Builder.load_string(KV)

    def on_start(self):
        if self.wallet.exists():
            self.root.ids.mainScrMan.current = "createWallet"
        else:
            self.root.ids.mainScrMan.current = "enterPassword"

    def on_stop(self):
        self.play = False
        del self.wallet

    def copyAddr(self):
        Clipboard.put(self.address)

    def updateBalance(self, password):
        while self.play:
            balance = self.wallet.walletBalance(password)
            usdBalance = self.wallet.balanceInUSD(balance)
            self.printBalance(balance, usdBalance)
            for i in range(15):
                if not(self.play):
                    break
                sleep(1)

    def changeWallet(self, walletName):
        self.wallet.changeWallet(walletName)
        self.root.ids.mainScrMan.current = "main"

    def updateChangeList(self):
        self.root.ids.scroll.clear_widgets()
        changelist = MDList()
        for wallet in self.wallet.getWalletList():
            changelist.add_widget(OneLineListItem(text=f"{wallet}", on_press=lambda x: self.changeWallet(x.text)))
        self.root.ids.scroll.add_widget(changelist)

    def getNewMnemonic(self):
        self.root.ids.mnemonicLabel.text = str(self.wallet.newWallet())

    def getNewMnemonic2(self):
        self.root.ids.mnemonicLabel2.text = str(self.wallet.newWallet())

    def importNewWallet(self, mnemonic, password, walletName):
        self.wallet.importNewWallet(walletName, mnemonic, password)

    def importWallet(self, mnemonic, password, walletName):
        self.wallet.importWallet(walletName, mnemonic, password)
        self.root.ids.mainScrMan.current = "enterPassword"

    def addChain(self, chainCoin, RPC_URL):
        self.wallet.addProvider(chainCoin, RPC_URL)

    def openWallet(self, password):
        self.wallet.importWalletFile()
        self.play = True
        self.address = self.wallet.walletAddress(password)
        self.balance_thread = threading.Thread(target=lambda: self.updateBalance(password), args=())
        self.balance_thread.start()

    def switchToSend(self, txt):
        self.coin = txt.split(":")[0]
        self.root.ids.balanceCoinView.text = txt
        self.root.ids.mainScrMan.current = "coin"

    def sendTokens(self, recipient, amount, password):
        if self.coin in providers:
            self.wallet.sendTo(recipient, amount, password, self.coin)
        else:
            self.wallet.sendToken(recipient, amount, password, self.coin)

    def addToken(self, tokenAddr, tokenChain):
        self.wallet.addToken(tokenAddr, tokenChain)

    def updateDropMenu(self):
        menu_items = []
        for chain in self.wallet.providers.keys():
            menu_items.append({
                "text": chain,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{chain}": self.root.ids.dropMenu.set_item(x),
            })
        self.menu = MDDropdownMenu(
            caller=self.root.ids.dropMenu,
            items=menu_items,
            width_mult=4,
        )

    @mainthread
    def printBalance(self, balance, usdBalance):
        self.root.ids.coinsView.clear_widgets()
        self.root.ids.balanceDollarView.text = str(usdBalance) + "$"
        for coin in balance:
            self.root.ids.coinsView.add_widget(OneLineListItem(text=f"{coin}: {balance[coin]}", on_press=lambda x: self.switchToSend(x.text)))

Walet().run()
