# 物理位置の対応

元は40位置、Cornixの定義はノブ押し込みを含む50位置です。
ZMKの `key-positions` は文字コードではなく、下表の **Cornix位置**を使います。
右手側をVialのマトリクス列番号のまま移すと左右反転するため、基板モジュールの
`cornix-layouts.dtsi` の順序に合わせています。

| 元の位置 | 元のキー | Cornix位置 |
|---|---|---|
| 0–9 | Q W E R T / Y U I O P | 1–10 |
| 10–19 | A S D F G / H J K L ; | 13–22 |
| 20–24 | Z X C V B | 25–29 |
| 25–29 | N M , . ' | 32–36 |
| 30–32 | Shift Alt Cmd | 38–40 |
| 33 | Space/Fn | 42 |
| 34 | Ctrl | 43 |
| 35–37 | Bksp Enter/Num Symbol | 44–46 |
| 38–39 | 右Alt /-Shift | 48–49 |

元の40位置に含まれない Cornix位置:

| Cornix位置 | 追加の割り当て |
|---|---|
| 0 / 11 | Esc / Bksp |
| 12 / 23 | Tab / Enter |
| 24 / 37 | 左Shift / /-Shift |
| 30 / 31 | 左ノブ押し込みミュート / 右ノブ押し込み中クリック |
| 41 / 47 | BTレイヤーを保持 / MOUSEレイヤーを保持 |

BTレイヤーの追加位置0はStudioのUnlock、11は `to 0`。
追加位置は元のコンボの構成キーには含めません。

標準RMKで読み取った設定では、左最内側が `LT(1,KC_SPACE)`、その左がCtrlでした。
今回のZMK配置はその2位置を交換しており、Spaceが42、Ctrlが43です。
