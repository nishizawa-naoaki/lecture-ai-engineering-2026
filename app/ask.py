import argparse
import os
import sys

from google import genai
from google.genai import errors

MODEL = os.getenv("AIE_MODEL", "gemini-3.8-flash")
DEFAULT_QUESTION = "LoRA とは何ですか?"


def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print(
            "[エラー] GEMINI_API_KEY が設定されていません。"
            "Codespaces secret に登録し、Codespace を再起動してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    # TODO(第1回 演習): response.usage_metadata から
    # 入力トークン数と出力トークン数を表示してみよう (Copilotに頼んでよい)
    if response.usage_metadata:
        print(f"[入力トークン数] {response.usage_metadata.prompt_token_count}")
        print(f"[出力トークン数] {response.usage_metadata.candidates_token_count}\n")

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print(f"[質問] {args.question}\n")
    try:
        print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))


def api_error_message(code: int, message: str) -> str:
    if code == 429:
        return (
            "[エラー] リクエスト制限 (429) に達しました。\n"
            "無料枠には 1 分あたり / 1 日あたりの上限があります。"
            "時間をおいて試すか、別のモデルを検討してください。"
        )
    return f"[APIエラー {code}] {message}"


if __name__ == "__main__":
    main()