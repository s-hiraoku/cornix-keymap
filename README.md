# Cornix LP — KobitoKey QWERTY / ZMK

macOS・US（ANSI）配列向けの Cornix LP 用 ZMK 設定です。
[KobitoKey_QWERTY](https://github.com/s-hiraoku/KobitoKey_QWERTY) の通常入力、
コンボ、長押し判定を Cornix の物理位置へ移植します。
**Space は左親指の中央、LCTRL はその右隣**です。

## キー配置

元の40キーだけを割り当てます。**通常・Fn・数字・記号・BT の5レイヤーと、
同時押しを1枚のSVGにまとめました。** 画像をクリックすると拡大できます。

[![Cornix LPの40キー配列：通常、Fn、数字、記号、BT、同時押し](docs/keymap.svg)](docs/keymap.svg)

- **キーの上段**：タップ時の入力、またはそのキーの動作。
- **青い下段**：長押し時の動作。例：`Space / L1 Fn` はタップで空白、長押しでFn。
- **灰色の下段**：動作の補足。BTの接続先選択・消去・通常へ戻るキーは、長押し不要です。
- **▽**：下位の有効なレイヤーを使う（キーの無効化ではありません）。
- **Symbol**：右親指の `RShift / L3 Symbol`。タップ側は右Shift、長押しで記号レイヤー。
  右端の `/ / RShift` は、タップで `/`、長押しで右Shiftです。
- **Alt = Option、Cmd = Command**。左Spaceだけ元の `retro-tap` を維持します。

各レイヤーは元の40キーを4行×左右5列に揃えた模式図です。
基板定義にある残り10位置（外周・追加親指位置・ノブ押し込み）は、
全5レイヤーで `&none`（無効）です。ノブ回転も無効です。

## 元設定から維持する動作とCornix向けの変更

- 参照コミット: `35b175d2717d9d09373212c6f93f6aa80deb338a`。
- 文字・Fn・数字・記号・BTのキー配置を移植。下記のY/H/P以外は対応する元のキー定義を保持します。
- 5コンボの操作・80/50ms判定・適用レイヤーを維持します。
- Space / Enter / Symbol / 右端 `/` の長押し判定も維持します。
  `180ms` / `quick-tap-ms=125` / `require-prior-idle-ms=90`、左Spaceだけの `retro-tap` も元と同じです。
- **Y・H・Pは通常の文字キー**です。長押しでも文字をリピートし、別レイヤーへ移動しません。
- **トラックボール専用の9レイヤーとマクロを削除**しました。
  Cornixにないセンサーを前提とするMOUSE / GESTURE / TAB / DESKTOP / ZOOM / DRAG /
  PRECISION / HSCROLL / SCROLL MENUは含めません。
- BTは元のLayer 8から**Layer 4**へ番号を整理しました。
  入口は元と同じ親指Bksp+Symbol、通常への復帰はLCtrl / RAltの位置です。
- 元の40キー以外の10位置、ノブ回転・押し込みは無効です。
  外周キーや追加のBT/MOUSEキー、Studio Unlockを割り当てません。

## ビルドと導入

[Actions](https://github.com/s-hiraoku/cornix-keymap/actions) の **Build Cornix ZMK** が、
入力検証後に左右のファームウェアと設定リセット用 UF2 をビルドします。
ZMK と Cornix の基板モジュールは `config/west.yml` でコミットを固定しています。
ルートの `Kconfig` は、この基板モジュールの Cornix 専用ボードに対し、
新しい ZMK CI が要求する `ZMK_BOARD_COMPAT` 宣言を補います。

| ファイル | 用途 |
|---|---|
| `cornix-left.uf2` | 左・セントラル。USB、Bluetooth、ZMK Studio |
| `cornix-right.uf2` | 右・ペリフェラル |
| `cornix-reset-left.uf2` | 左の設定消去専用。通常入力用ではない |
| `cornix-reset-right.uf2` | 右の設定消去専用。通常入力用ではない |

**書き込み前に [移行・復元手順](docs/migration.md) を確認してください。**
ビルド成功は、手元の本体・ブートローダーとの適合や実機動作の確認ではありません。

## AI と設定を変更する

1. `tests/fixtures/KobitoKey.keymap` は参照元の記録として保持する。
   Cornix向けの位置対応・文字キー化・採用レイヤーは `scripts/import_kobitokey.py` で管理する。
2. `python3 scripts/import_kobitokey.py` で `config/cornix.keymap` を生成する。
3. `python3 scripts/render_keymap.py` でREADME用のSVGを更新する。
4. `python3 -m unittest discover -s tests -v` で参照元・物理位置との整合を確認する。
   SVGの更新漏れは `python3 scripts/render_keymap.py --check` で確認できる。
5. Git に保存し、Actions のビルド結果を確認する。

参照 fixture はリポジトリ内に保存してあり、ビルド時に元リポジトリの main を取得しません。
意図してコンボ・長押し仕様を変更した場合は、該当する検証もその意図に合わせて更新します。

ZMK へ移行後、Vial/vitaly の `.vil` は ZMK には適用できません。
配置確認には [ZMK Studio](https://zmk.studio/) を使います。
元の40キーには Studio Unlock がないため、解除用のキーやコンボは追加しません。
コンボ、長押し判定、マクロはソースで管理します。
Studio の **Save** で配置を変更すると保存済み配置がソースより優先されるため、
ソース変更を反映させるときは Studio の **Restore Stock Settings** が必要です。
解除用キーが実機にない場合、保存済み配置を消すには設定リセット用 UF2 を使います。
この方法はペアリングも消すため、更新手順の注意事項を確認してください。
Studio で設定を変更していなければ、設定リセットは不要です。

## 参照

- [元の KobitoKey 設定](https://github.com/s-hiraoku/KobitoKey_QWERTY)
- [Cornix 基板モジュール・移行の注意点](https://github.com/numachang/cornix-zmk-custom/blob/ade15a303257ffb2c11357839ff39199b863b087/README_ja.md)
- [ZMK Studio の機能と保存済み配置](https://zmk.dev/docs/features/studio)
- [Cornix メーカーの標準ファームウェア](https://docs.channel.io/jezailfunderjp/ja/articles/Cornix-ファームウェア-bf1534b6)
