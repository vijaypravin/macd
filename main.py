import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import mysql.connector

def show_popup(title, message):
    popup_html = f"""
    <div id="popup" style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: white;
        border: 1px solid #ccc;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        z-index: 1000;
    ">
        <h2>{title}</h2>
        <p>{message}</p>
        <button onclick="document.getElementById('popup').style.display='none'">Close</button>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            document.getElementById('popup').style.display = 'block';
        }});
    </script>
    """
    components.html(popup_html, height=200)

def check_macd():
    try:
        mydb = mysql.connector.connect(
            user="",
            password="1L0",
            host="macd.mysql.database.azure.com",
            port=3306,
            database="macd_db",
            # ssl_ca="DigiCertGlobalRootCA.crt.pem"  # Ensure this path is correct!
        )
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM macd")
        result = mycursor.fetchall()

        if result:  # Check if there are any results
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
                            show_popup("Alert", f'Nifty: {current_price} \n BuyCE: {buyce}')
                        else:
                            remainder = buyce % 100
                            if remainder >= 50:
                                rounded_buyce = (buyce // 100 + 1) * 100
                            else:
                                rounded_buyce = (buyce // 100) * 100
                            st.write(f'(Nifty: {current_price}) \n BuyCE: {rounded_buyce}')
                elif (previous_macd_value > 0 and macd_value <= 0):
                    st.write("Sign change detected!")
                    symbols = ['^NSEI']
                    for symbol in symbols:
                        stock = yf.Ticker(symbol)
                        current_price = stock.info.get('regularMarketPrice')
                        buype = int(current_price + 200)
                        if buype % 100 == 0:
                            show_popup("Alert", f'Nifty: {current_price} BuyPE: {buype}')
                        else:
                            remainder = buype % 100
                            if remainder >= 50:
                                rounded_buyce = (buype // 100 + 1) * 100
                            else:
                                rounded_buyce = (buype // 100) * 100
                            st.write(f'({symbol}: {current_price}) BuyPE: {rounded_buyce}')
            # Store the current macd value for the next iteration.
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
    check_macd()
