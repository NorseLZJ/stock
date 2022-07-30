from stock_data import *

if __name__ == '__main__':
    # code = ['002424', '601611', '600115', '300059', '000881', '002401', '600682', '000725']
    code = ['002424']
    # 放txt
    if not os.path.exists('opt'):
        os.mkdir('opt')

    for i in code:
        cent, bill_cent = StockData(i).get_content()
        with open(format("%s/%s.txt" % ('opt', i)), 'w', encoding='utf8') as f:
            f.write(cent)

        with open(format("%s/%s.bill.txt" % ('opt', i)), 'w', encoding='utf8') as f:
            f.write(bill_cent)
