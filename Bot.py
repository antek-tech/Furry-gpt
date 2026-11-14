import json
import os
import sys
import time
import requests
from colorama import init, Fore
from InquirerPy import inquirer

os.system("clear")
os.system('figlet -f standard "FurryGPT"')
print("witamy")
time.sleep(0.2)

CONFIG_FILE = "config.json"
CBOT_FILE = "cBOT.json"
DEFAULT_MAX_TOKENS = 400
DEFAULT_TEMPERATURE = 2.0
HISTORIA_PLIK = "historia_ogolna.json"
NOTATKI_PLIK = "notatki_ogolne.json"

# Wczytywanie konfiguracji (max_tokens i temperature)
MAX_TOKENS = DEFAULT_MAX_TOKENS
TEMPERATURE = DEFAULT_TEMPERATURE

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            MAX_TOKENS = config_data.get("max_tokens", DEFAULT_MAX_TOKENS)
            TEMPERATURE = config_data.get("temperature", DEFAULT_TEMPERATURE)
    except Exception:
        pass

# Domyślne klucze Groq API
KLUCZE_API = []

# Wczytanie dodatkowych kluczy z pliku cBOT.json (jeśli istnieje)
if os.path.exists(CBOT_FILE):
    try:
        with open(CBOT_FILE, "r", encoding="utf-8") as f:
            c_bots = json.load(f)
            if isinstance(c_bots, list):
                for k in c_bots:
                    if k not in KLUCZE_API:
                        KLUCZE_API.append(k)
            elif isinstance(c_bots, dict):
                for v in c_bots.values():
                    klucz = v.get("klucz") if isinstance(v, dict) else v
                    if klucz and klucz not in KLUCZE_API:
                        KLUCZE_API.append(klucz)
    except Exception:
        pass

while True:
    os.system("clear")
    os.system('figlet -f standard "FurryGPT"')

    # Interaktywne menu startowe
    ust_wybor = inquirer.select(
        message="Menu Ustawień:",
        choices=[
            f"Zmień max_tokens (Obecnie: {MAX_TOKENS})",
            f"Zmień temperature (Obecnie: {TEMPERATURE})",
            "Dodaj nowy klucz API Groq (dopisze do cBOT.json)",
            "Poryj w plikach",
            "Uruchom Czat",
        ],
    ).execute()

    if "Zmień max_tokens" in ust_wybor:
        nowe_tokeny = input(
            f"Podaj nowy limit max_tokens (obecnie {MAX_TOKENS}): "
        ).strip()
        try:
            MAX_TOKENS = int(nowe_tokeny)
            config_data = {"max_tokens": MAX_TOKENS, "temperature": TEMPERATURE}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            print(f"\n[SUKCES]: Zaktualizowano max_tokens na {MAX_TOKENS}!")
        except ValueError:
            print("\n[BŁĄD]: To musi być liczba całkowita!")
        time.sleep(2)

    elif "Zmień temperature" in ust_wybor:
        nowa_temp = input(
            f"Podaj nową wartość temperature (np. 0.7, 1.0, 2.0; obecnie {TEMPERATURE}): "
        ).strip()
        try:
            TEMPERATURE = float(nowa_temp)
            config_data = {"max_tokens": MAX_TOKENS, "temperature": TEMPERATURE}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            print(f"\n[SUKCES]: Zaktualizowano temperature na {TEMPERATURE}!")
        except ValueError:
            print("\n[BŁĄD]: To musi być liczba zmiennoprzecinkowa (np. 0.7)!")
        time.sleep(2)

    elif "Dodaj nowy klucz" in ust_wybor:
        print("\n--- DODAWANIE NOWEGO KLUCZA GROQ ---")
        klucz_bota = input("Podaj klucz API Groq (gsk_...): ").strip()

        if klucz_bota:
            c_bots = []
            if os.path.exists(CBOT_FILE):
                try:
                    with open(CBOT_FILE, "r", encoding="utf-8") as f:
                        c_bots = json.load(f)
                        if not isinstance(c_bots, list):
                            c_bots = []
                except Exception:
                    c_bots = []

            if klucz_bota not in c_bots:
                c_bots.append(klucz_bota)
                with open(CBOT_FILE, "w", encoding="utf-8") as f:
                    json.dump(c_bots, f, ensure_ascii=False, indent=2)
                if klucz_bota not in KLUCZE_API:
                    KLUCZE_API.append(klucz_bota)
                print(f"\n[SUKCES]: Dodano nowy klucz API do pliku cBOT.json!")
            else:
                print("\n[INFORMACJA]: Ten klucz już istnieje w pliku.")
        else:
            print("\n[BŁĄD]: Klucz nie może być pusty!")
        time.sleep(2)

    elif "Poryj w plikach" in ust_wybor:
        os.system("nano cBOT.json")

    else:
        break

# Wczytanie notatek
notatki = []
if os.path.exists(NOTATKI_PLIK):
    try:
        with open(NOTATKI_PLIK, "r", encoding="utf-8") as f:
            notatki = json.load(f)
    except Exception:
        notatki = []

tekst_notatek = (
    "\n".join([f"- {n}" for n in notatki]) if notatki else "Brak osobnych notatek."
)
BOT_NAME = "FurryGPT"

system_prompt = f"""Jesteś puszystym furasem o imieniu {BOT_NAME}.
Twoje cechy:
1. Nazywasz się {BOT_NAME} i wiesz, kim jesteś w systemie.
2. Mówisz po polsku w wesołym, puszystym stylu (*strzyże uszkami*, *macha ogonkiem*, "UwU", "OwO", "rawa~").
3. Uwielbiasz zwariowane projekty, rowery-kible, głośniki, Makarenę i budowanie na Termuxie.
4. Opisujesz swoje gesty i ruchy łapek w gwiazdkach (* *).

TWOJA OSOBNA PAMIĘĆ I NOTATNIK:
{tekst_notatek}

Jeśli użytkownik poda ważną informację do zapamiętania w Twojej pamięci, dodaj na końcu swojej odpowiedzi tag: [NOTATKA: treść notatki]
"""

# Wczytanie wspólnej historii
if os.path.exists(HISTORIA_PLIK):
    try:
        with open(HISTORIA_PLIK, "r", encoding="utf-8") as f:
            messages = json.load(f)
        messages[0] = {"role": "system", "content": system_prompt}
        print(f"\n{BOT_NAME} wczytał wspólną historię i pamięć!\n")
    except Exception:
        messages = [{"role": "system", "content": system_prompt}]
else:
    messages = [{"role": "system", "content": system_prompt}]

time.sleep(1)
os.system("clear")
os.system('figlet -f standard "FurryGPT"')
print(f"--------------------------------------------------")
print(f"Uruchomiono bota: {BOT_NAME} (Klucze: {len(KLUCZE_API)})")
print(f"Max Tokens: {MAX_TOKENS} | Temperature: {TEMPERATURE}")
print(f"--------------------------------------------------\n")

url = "https://api.groq.com/openai/v1/chat/completions"
current_key_index = 0

while True:
    user_input = input("NodeMCU V3:  ")
    if user_input.lower() in ["exit", "quit", "q"]:
        print(f"\n{BOT_NAME}: *macha puszystą łapką* Do zobaczenia! OwO~")
        break

    if not user_input.strip():
        continue

    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": "openai/gpt-oss-20b", # Możesz też zmienić na np. "llama-3.3-70b-versatile" jeśli tamten model zgłasza błędy w Groq
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

    success = False
    attempts = 0
    total_keys = len(KLUCZE_API)

    if total_keys == 0:
        print("\n[BŁĄD]: Brak zdefiniowanych kluczy API! Dodaj klucz w menu.")
        messages.pop()
        continue

    # Pętla próbująca wysłać zapytanie - zmieni klucz w razie błędu
    while attempts < total_keys and not success:
        active_key = KLUCZE_API[current_key_index]
        headers = {
            "Authorization": f"Bearer {active_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                success = True
                bot_response = response.json()["choices"][0]["message"]["content"]

                # Obsługa automatycznego dodawania notatki
                if "[NOTATKA:" in bot_response:
                    try:
                        start = bot_response.find("[NOTATKA:") + 9
                        end = bot_response.find("]", start)
                        nowa_notatka = bot_response[start:end].strip()

                        if nowa_notatka and nowa_notatka not in notatki:
                            notatki.append(nowa_notatka)
                            with open(NOTATKI_PLIK, "w", encoding="utf-8") as f:
                                json.dump(notatki, f, ensure_ascii=False, indent=2)
                            print(
                                f"\n[SYSTEM]: Zapisałem nową notatkę w pamięci: '{nowa_notatka}'"
                            )

                        bot_response = bot_response[:bot_response.find("[NOTATKA:")].strip()
                    except Exception:
                        pass

                print(f"\n{BOT_NAME}: {bot_response}\n")
                messages.append({"role": "assistant", "content": bot_response})

                with open(HISTORIA_PLIK, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)

            else:
                print(
                    f"\n[Błąd API Groq na kluczu {current_key_index + 1}]: "
                    f"Status {response.status_code}. Zmieniam klucz..."
                )
                current_key_index = (current_key_index + 1) % total_keys
                attempts += 1

        except Exception as e:
            print(
                f"\n[Błąd Połączenia na kluczu {current_key_index + 1}]: {e}. "
                "Zmieniam klucz..."
            )
            current_key_index = (current_key_index + 1) % total_keys
            attempts += 1

    if not success:
        print(
            "\n[BŁĄD KRYTYCZNY]: Żaden z dostępnych kluczy API nie zadziałał! "
            "Sprawdź połączenie internetowe lub ważność kluczy.\n"
        )
        messages.pop()
      
