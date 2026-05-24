import tkinter as tk
from tkinter import messagebox
import requests

# --- Configuration ---
# API Key from the original file. Please replace with your actual key for robust use.
API_KEY = "4a6c38aa357a77beb54f0ac1"
API_BASE_URL = "https://v6.exchangerate-api.com/v6"

def convert_currency():
    """Fetches exchange rate and calculates the converted amount."""
    try:
        amount = float(entry_amount.get())
        from_currency = entry_from.get().strip().upper()
        to_currency = entry_to.get().strip().upper()
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for the amount.")
        return

    if not from_currency or not to_currency or len(from_currency) != 3 or len(to_currency) != 3:
        messagebox.showerror("Input Error", "Please enter valid 3-letter currency codes (e.g., USD, EUR).")
        return

    # Update button state to show loading
    convert_button.config(text="Converting...", state=tk.DISABLED)
    result_var.set("Fetching rates...")

    url = f"{API_BASE_URL}/{API_KEY}/latest/{from_currency}"

    # --- API Call with Simple Retry Logic (for robustness) ---
    max_retries = 3
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Will raise an HTTPError if the status code is 4XX or 5XX
            data = response.json()

            if data["result"] == "success":
                rates = data.get("conversion_rates")
                if rates and to_currency in rates:
                    rate = rates[to_currency]
                    converted_amount = round(amount * rate, 2)
                    
                    result_text = f"{amount:,.2f} {from_currency} = {converted_amount:,.2f} {to_currency}"
                    rate_info = f"(Rate: 1 {from_currency} = {rate:.4f} {to_currency})"
                    
                    result_var.set(f"{result_text}\n{rate_info}")
                    break  # Success, exit the loop
                else:
                    messagebox.showerror("Conversion Error", f"Currency code '{to_currency}' not supported or rate data is missing.")
                    break
            else:
                # Handle API-specific errors
                error_type = data.get("error-type", "Unknown API error")
                messagebox.showerror("API Error", f"Conversion failed: {error_type}. Check your API key and currency code.")
                break

        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                # Simple backoff delay for retries
                root.after(1000 * (2 ** i), lambda: None) # Wait 1, 2, 4 seconds...
                continue
            else:
                messagebox.showerror("Network Error", f"Could not connect to the currency API: {e}")
                break
        except Exception as e:
            messagebox.showerror("An unexpected error occurred", str(e))
            break
            
    # Restore button state
    convert_button.config(text="Convert", state=tk.NORMAL)

def swap_currencies():
    """Swaps the content of the 'from' and 'to' currency fields."""
    from_val = entry_from.get()
    to_val = entry_to.get()
    entry_from.delete(0, tk.END)
    entry_from.insert(0, to_val)
    entry_to.delete(0, tk.END)
    entry_to.insert(0, from_val)
    # Trigger conversion after swap
    convert_currency()

# --- GUI Setup (Tkinter) ---

# 1. Main Window
root = tk.Tk()
root.title("Python Currency Converter")
root.geometry("450x300")
root.resizable(False, False)
root.iconify() # Optional: Hide the default icon in some OS

# 2. Styling (Simple internal styling for Tkinter)
PAD_X = 15
PAD_Y = 10
FONT_LARGE = ('Arial', 14, 'bold')
FONT_MEDIUM = ('Arial', 10)

# 3. Widgets

# Title
title_label = tk.Label(root, text="Real-Time Currency Converter", font=FONT_LARGE)
title_label.pack(pady=(20, 10))

# Amount Input
frame_amount = tk.Frame(root)
frame_amount.pack(pady=5, padx=PAD_X, fill='x')
tk.Label(frame_amount, text="Amount:", font=FONT_MEDIUM).pack(side=tk.LEFT)
entry_amount = tk.Entry(frame_amount, width=10, font=FONT_MEDIUM, justify='center')
entry_amount.insert(0, "100.00")
entry_amount.pack(side=tk.LEFT, fill='x', expand=True, padx=(5, 0))

# Currency Inputs and Swap Button
frame_currencies = tk.Frame(root)
frame_currencies.pack(pady=5, padx=PAD_X, fill='x')

# From Currency
tk.Label(frame_currencies, text="From:", font=FONT_MEDIUM).pack(side=tk.LEFT, padx=(0, 5))
entry_from = tk.Entry(frame_currencies, width=6, font=FONT_MEDIUM, justify='center')
entry_from.insert(0, "USD")
entry_from.pack(side=tk.LEFT)

# Swap Button
swap_button = tk.Button(frame_currencies, text="⇄", command=swap_currencies, font=('Arial', 12, 'bold'))
swap_button.pack(side=tk.LEFT, padx=10)

# To Currency
tk.Label(frame_currencies, text="To:", font=FONT_MEDIUM).pack(side=tk.LEFT, padx=(10, 5))
entry_to = tk.Entry(frame_currencies, width=6, font=FONT_MEDIUM, justify='center')
entry_to.insert(0, "EUR")
entry_to.pack(side=tk.LEFT)


# Convert Button
convert_button = tk.Button(root, text="Convert", command=convert_currency, font=FONT_MEDIUM, bg='#3b82f6', fg='white', activebackground='#2563eb', activeforeground='white')
convert_button.pack(pady=10, padx=PAD_X, fill='x')

# Result Display
result_var = tk.StringVar()
result_var.set("Enter details and click Convert.")
result_label = tk.Label(root, textvariable=result_var, font=('Arial', 12), fg='#1f2937', height=3, relief=tk.SUNKEN, bd=1)
result_label.pack(pady=(5, 20), padx=PAD_X, fill='x')

# Run initial conversion on start
root.after(100, convert_currency)

# 4. Main Loop
root.mainloop()