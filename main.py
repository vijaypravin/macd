import streamlit as st
import yfinance as yf
import mysql.connector
import requests
import time


def check_macd():
    try:
        mydb = mysql.connector.connect(
            user="adminh0st1ng",
            password="1L0@dm1n",
            host="macd.mysql.database.azure.com",
            port=3306,
            database="macd_db",
        )
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM macd")
        result = mycursor.fetchall()

        if result:
            macd_value = float(result[0][0])
            st.write(f"Nifty50 Macd Current value: {macd_value}")
            try:
                with open("previous_macd.txt", "r") as f:
                    previous_macd_value = float(f.read().strip())
            except FileNotFoundError:
                previous_macd_value = None

            if previous_macd_value is not None:
                if (previous_macd_value < 0 and macd_value >= 0):
                    st.write("Sign change detected!")
                    symbols = ['^NSEI']
                    for symbol in symbols:
                        stock = yf.Ticker(symbol)
                        current_price = stock.info.get('regularMarketPrice')
                        buyce = int(current_price - 200)
                        if buyce % 100 == 0:
                            requests.post("https://ntfy.sh/Macd", data=f'Nifty: {current_price} BuyCE: {buyce}'.encode(encoding='utf-8'))
                            requests.post("https://ntfy.sh/Pasu", data=f'Nifty: {current_price} BuyCE: {buyce}'.encode(encoding='utf-8'))
                        else:
                            remainder = buyce % 100
                            if remainder >= 50:
                                rounded_buyce = (buyce // 100 + 1) * 100
                            else:
                                rounded_buyce = (buyce // 100) * 100
                            requests.post("https://ntfy.sh/Macd", data=f'Nifty: {current_price} BuyCE: {rounded_buyce}'.encode(encoding='utf-8'))
                            requests.post("https://ntfy.sh/Pasu", data=f'Nifty: {current_price} BuyCE: {rounded_buyce}'.encode(encoding='utf-8'))
                elif (previous_macd_value > 0 and macd_value <= 0):
                    st.write("Sign change detected!")
                    symbols = ['^NSEI']
                    for symbol in symbols:
                        stock = yf.Ticker(symbol)
                        current_price = stock.info.get('regularMarketPrice')
                        buype = int(current_price + 200)
                        if buype % 100 == 0:
                            requests.post("https://ntfy.sh/Macd", data=f'Nifty: {current_price} BuyPE: {buype}'.encode(encoding='utf-8'))
                            requests.post("https://ntfy.sh/Pasu", data=f'Nifty: {current_price} BuyPE: {buype}'.encode(encoding='utf-8'))
                        else:
                            remainder = buype % 100
                            if remainder >= 50:
                                rounded_buyce = (buype // 100 + 1) * 100
                            else:
                                rounded_buyce = (buype // 100) * 100
                            requests.post("https://ntfy.sh/Macd", data=f'Nifty: {current_price} BuyPE: {rounded_buyce}'.encode(encoding='utf-8'))
                            requests.post("https://ntfy.sh/Pasu", data=f'Nifty: {current_price} BuyPE: {rounded_buyce}'.encode(encoding='utf-8'))
            with open("previous_macd.txt", "w") as f:
                f.write(str(macd_value))
        else:
            st.write("No data found in the macd table.")

        mycursor.close()
        mydb.close()
    except mysql.connector.Error as err:
        st.error(f"Error connecting to database or processing data: {err}")
    except ValueError as ve:
        st.error(f"Error parsing macd value: {ve}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

st.title("MACD Analysis")

if st.button("Check MACD"):
    while True:
        check_macd()
