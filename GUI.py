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

import crypto

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
                        app.sendButtonClick(recipient_field.text, amount_field.text)
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
        self.wallet = crypto.WalletCore()
        self.theme_cls.primary_palette = "Indigo"
        return Builder.load_string(KV)

    def on_start(self):
        address = self.wallet.walletAddress()
        balance = self.wallet.walletBalance()
        self.root.ids.address_label.text = address
        for coin in balance:
            self.root.ids.card.ids.balance.add_widget(OneLineListItem(text=f"{coin}: {balance[coin]}"))

    def sendButtonClick(self, recipient, amount):
        self.wallet.sendTo(recipient, amount)

Walet().run()
