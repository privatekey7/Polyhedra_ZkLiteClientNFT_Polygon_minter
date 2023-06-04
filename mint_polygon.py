from web3 import Web3
import time
import sys
import random
import inquirer

time_delay_min = 30
time_delay_max = 60


def read_abi_from_file(file_name):
    with open(file_name, "r") as f:
        return f.read()


def mint(private_key, delay_enabled=False, delay_on_success=False):
    try:
        web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/polygon'))
        address_wallet = web3.eth.account.from_key(private_key).address
        print(f'{address_wallet} - минт')

        address_contract = Web3.to_checksum_address('0x6b0c248679f493481411a0a14cd5fc2dbbe8ab02')
        abi = read_abi_from_file('abi.txt')
        contract = web3.eth.contract(address=address_contract, abi=abi)

        if contract.functions.balanceOf(address_wallet).call() > 0:
            print(f'{address_wallet} - уже сминчено')
        else:
            dick = {
                'from': address_wallet,
                'nonce': web3.eth.get_transaction_count(address_wallet),
                'gasPrice': web3.eth.gas_price
            }
            tx = contract.functions.mint().build_transaction(dick)
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)

            raw_tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash = web3.to_hex(raw_tx_hash)

            tx_receipt = web3.eth.wait_for_transaction_receipt(raw_tx_hash, timeout=300)
            if tx_receipt.status == 1:
                print(f'{address_wallet} - минт успешен')
                if delay_on_success:
                    delay = random.randint(time_delay_min, time_delay_max)
                    print(f"Следующий минт через {delay} секунд")
                    time.sleep(delay)
            else:
                print(f'{address_wallet} - минт неудался')
                return

        completed_mints.append(private_key)

    except ValueError as error:
        print(f"{address_wallet} - не хватает газа")
        return


if __name__ == '__main__':
    with open('keys.txt', 'r') as f:
        keys_list = [line.strip() for line in f]

    questions = [
        inquirer.List('enable_delay',
                      message="Хотите включить задержку между минтами?",
                      choices=['Да', 'Нет'],
                      ),
    ]

    answers = inquirer.prompt(questions)
    enable_delay = answers['enable_delay'] == 'Да'

    completed_mints = []

    while len(completed_mints) < len(keys_list):
        private_key = random.choice(keys_list)
        if private_key in completed_mints:
            continue
        mint(private_key, delay_enabled=enable_delay, delay_on_success=True)

        if enable_delay and private_key not in completed_mints:
            delay = random.randint(time_delay_min, time_delay_max)
            print(f"Следующий минт через {delay} секунд")
            time.sleep(delay)
    
    print('Все минты выполнены')
    sys.exit()