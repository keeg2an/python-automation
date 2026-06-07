# python-automation

Python を用いた業務自動化スクリプト集。定型作業の自動化・データ処理・外部サービス連携などを行う。

## プロジェクト概要

- ファイル操作・データ集計などの定型作業の自動化
- 外部 API・Web サービスとの連携スクリプト
- 定期実行タスク（スケジューラ連携）

## 技術スタック

- Python 3.x
- venv（仮想環境管理）
- pip + requirements.txt（依存関係管理）

## ディレクトリ構成

```
python-automation/
├── CLAUDE.md
├── requirements.txt   # 依存パッケージ
├── .env.example       # 環境変数のサンプル（APIキー等）
└── src/               # スクリプト本体
```

## 開発環境セットアップ

```powershell
# 仮想環境を作成・有効化
python -m venv venv
.\venv\Scripts\Activate.ps1

# 依存パッケージをインストール
pip install -r requirements.txt

# .env を作成し必要な環境変数を設定
cp .env.example .env
```

## Git 運用ルール

### コード変更のたびに GitHub へプッシュする

ファイルを変更・追加したら、**必ずその都度** 以下の手順で GitHub に反映する。

```powershell
# 変更内容を確認
git status
git diff

# 変更をステージング（claudeApp/python-automation/ 配下の変更ファイルを明示的に指定する）
git add claudeApp/python-automation/<変更したファイル>

# コミット（変更内容を日本語で簡潔に要約）
git commit -m "feat: ○○機能を追加"

# GitHub へプッシュ
git push origin master
```

> **注意**: このリポジトリのルートは `claudeApp/python-automation/` ではなく「ドキュメント」フォルダ全体になっている。`git add .` や `git add -A` は使わず、必ず `claudeApp/python-automation/` 配下の変更ファイルをパスで明示的に指定すること（個人ファイルの誤コミット防止）。

### コミットメッセージの種別プレフィックス

| プレフィックス | 用途 |
|---|---|
| `feat:` | 新機能の追加 |
| `fix:` | バグ修正 |
| `refactor:` | 動作を変えないコード改善 |
| `chore:` | 設定ファイル・依存関係などの変更 |
| `docs:` | ドキュメントのみの変更 |

### 注意事項

- APIキー・認証情報などの機密情報は `.env` に保存し、`.gitignore` に追加してコミットしない
- `.env.example` には実際の値を含めず、キー名のみを記載する

## コーディング方針

- コメントは「なぜそうするか（Why）」が自明でない箇所にのみ記載する
- エラーハンドリングはユーザー入力・外部 API など境界値にのみ行う
- 抽象化は実際に複数箇所で共通化が必要になってから検討する
