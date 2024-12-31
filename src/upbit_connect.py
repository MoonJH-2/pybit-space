import os
import pyupbit
from dotenv import load_dotenv


def upbit_connect():
    """
    Connect to Upbit using API keys stored in the .env file.
    Prints the KRW balance and cryptocurrency balances (currency and balance only).
    """
    # .env 파일 경로를 지정
    dotenv_path = os.path.join(os.path.dirname(__file__), "../configs/.env")
    load_dotenv(dotenv_path)

    # 환경 변수에서 API 키 로드
    access = os.getenv("UPBIT_ACCESS_KEY")
    secret = os.getenv("UPBIT_SECRET_KEY")

    # Upbit 객체 생성
    if not access or not secret:
        raise ValueError("API keys are missing. Check your .env file.")

    upbit = pyupbit.Upbit(access, secret)

    # KRW 잔고 출력
    # krw_balance = upbit.get_balance("KRW")
    # print(f"KRW Balance: {krw_balance}")

    # 보유 중인 모든 암호화폐의 잔고 및 단가 정보 조회
    all_balances = upbit.get_balances()

    # Currency와 Balance 데이터만 추출
    crypto_data = [
        {"currency": item["currency"], "balance": float(item["balance"])}
        for item in all_balances
        if float(item["balance"]) > 0  # 잔고가 0 이상인 경우만
    ]

    # 출력
    print("\n[Cryptocurrency Balances]")
    for item in crypto_data:
        print(f"Currency: {item['currency']}, Balance: {item['balance']:.6f}")

    return crypto_data


# 함수 호출
if __name__ == "__main__":
    upbit_connect()
