from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, portrait, letter, A3, A4, A5
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Flowable
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import pandas as pd
import sys
from MCLine import MCLine

def add_campaign():
    dfCampaigns = pd.read_csv('data/campaigns.csv',sep='\t').set_index('id')
    dfBrands = pd.read_csv('data/brands.csv', sep='\t')
    c_id = len(dfCampaigns)

    print(dfBrands.set_index('id')['name'].to_string())
    b_id = -1
    while b_id not in dfBrands['id'].unique():
        b_id = int(input('brand id:'))

    description = input('campaign description:')

    req_date = input('request date:')

    del_date = input('delivery date:')

    cat_req_date = input('catalog request date:')

    cat_del_date = input('catalog delivery date:')

    dfCampaigns.loc[c_id] = [b_id, description, req_date, del_date,
                            cat_req_date, cat_del_date]

    dfCampaigns.to_csv('data/campaigns.csv',sep='\t')

    return c_id


def find_product(brand_id, code):
    dfProducts = pd.read_csv('data/products.csv', sep='\t').set_index(['brand_id', 'code'])
    print(brand_id, code)
    try:
#         print(dfProducts.loc[(brand_id, code),['description', 'cost_price', 'sale_price']].to_string())
        return (dfProducts.loc[(brand_id, code)][['description','cost_price','sale_price']])
    except KeyError:
        print('Product not found')

def add_product():
    dfProducts = pd.read_csv('data/products.csv', sep='\t').set_index('id')
    dfCampaigns = pd.read_csv('data/campaigns.csv',sep='\t')

    if len(dfCampaigns > 0):
        print(dfCampaigns[['id', 'description']].to_string(index=False))
        campaign_id = int(input('Campaign id (enter to register new campaign):'))
#         if not campaign_id:
#             campaign_id = add_campaign()
    else:
        print('There is no campaign registered.')
        campaign_id = input('Do you want to continue and register a new campaign?'
                            +'(enter to continue/ 0 to finish)')
        if campaign_id:
            sys.exit
        else:
            campaign_id = add_campaign()

    insert = True
    while insert:
        p_id = len(dfProducts)
        p_brand_id = dfCampaigns.set_index('id').loc[campaign_id]['brand_id']
        p_page = input('page:')
        p_code = input('code:')

        product = find_product(int(p_brand_id), int(p_code))

        if product:
            ans = input('cost price (or enter to R${}):'
                        .format(str(product.loc[int(p_brand_id), int(p_code)]['cost_price'])))
            if ans:
                p_cost = float(ans)
            else:
                p_cost = float(product.loc[int(p_brand_id), int(p_code)]['cost_price'])
        else:
            p_cost = float(input('cost price:'))


        p_sale = -1
        while p_sale < p_cost:
            if product:
                ans = input('sale price (or enter to R${}):'
                        .format(str(product.loc[int(p_brand_id), int(p_code)]['sale_price'])))

                if ans:
                    p_sale = float(ans)
                else:
                    p_sale = float(product.loc[int(p_brand_id), int(p_code)]['sale_price'])
            else:
                p_sale = float(input('sale price:'))

        p_profit = float(p_sale) - float(p_cost)


        if product:
            ans = input('description (or enter to "{}"):'
                        .format(str(product.loc[int(p_brand_id), int(p_code)]['description'])))

            if ans:
                p_description = ans
            else:
                p_description = product.loc[int(p_brand_id), int(p_code)]['description']
        else:
            p_description = input('description:')

        dfProducts.loc[p_id]=[p_brand_id, campaign_id,
                              p_page, p_code, p_description,
                              p_cost, p_sale, p_profit
                             ]
        insert = not bool(input('Insert new product? (yes: enter/no: any key)'))
        dfProducts['profit'] = round(dfProducts['profit'],2)
#         print(dfProducts.to_string())
        dfProducts.reset_index().to_csv('data/products.csv',
                                        sep='\t', index=False)

def add_client():

    def add_discount(clientId, dfClients):
        dfDiscounts = pd.read_csv('data/discounts.csv', sep='\t')
        dfBrands = pd.read_csv('data/brands.csv', sep='\t')

        for index, row in dfBrands.iterrows():
            brandId = row['id']
            discount = 1
            while float(discount) > float(row['profit']):
                print('\n{}\'s profit: {}'.format(row['name'], row['profit']))
                discount = input('{}\'s discount to {} (0 - 1):'
                                 .format(dfClients.loc[clientId]['name'],
                                         dfBrands.loc[brandId]['name']))
            dfDiscounts = dfDiscounts.set_index(['client_id', 'brand_id'])
            dfDiscounts.loc[(clientId, brandId), 'discount'] = discount
            dfDiscounts = dfDiscounts.reset_index()
            dfDiscounts.to_csv('data/discounts.csv', sep='\t', index=False)
        print(dfDiscounts)

    dfClients = pd.read_csv('data/clients.csv', sep='\t')
    print('Registered clients:')
    print(dfClients.to_string())
    dfRevendors = pd.read_csv('data/revendors.csv', sep='\t')
    clientName = input('Client name:')

    print('Revendors:')
    for index, row in dfRevendors.iterrows():
        print('{} - {}'.format(row['id']+1, row['name']))
#     print('0 - new revendor')

    revendorId = -1

    while revendorId not in (list(dfRevendors['id'].unique())):
        revendorId = (int(input('Choose {}\'s revendor:'.format(clientName)))-1)

    clientId = len(dfClients)

#     if revendorId != 0:
    print(dfClients.to_string())

    dfClients = dfClients.set_index('id')
    dfClients.loc[clientId] = [clientName, revendorId]
#     TODO: else:
#         new_revendor()

#     dfClients = dfClients.reset_index()

    add_discount(clientId, dfClients)

    dfClients.to_csv('data/clients.csv', sep='\t')
    print(dfClients.to_string())

    return clientId, dfClients

def update_orders():
    dfItems = pd.read_csv('data/items.csv', sep='\t')
    dfCampaigns = pd.read_csv('data/campaigns.csv',sep='\t').set_index('id')
    dfClients = pd.read_csv('data/clients.csv', sep='\t')

    def compute_final_price(x, product_id):
        sale_price = float(dfProducts.loc[product_id]['sale_price'])
        return round(sale_price*(1 - x['discount']), 2)*x['quantity']

    dfProducts = pd.read_csv('data/products.csv', sep='\t').set_index('id')

    dfItems['final_price'] = (dfItems
                              .apply(lambda x:
                                     compute_final_price(x,
                                                         int(x['product_id'])),
                                     axis=1))
    dfItems['client_name'] = (dfItems['client_id']
                              .apply(lambda x: (dfClients.set_index('id')
                                                .loc[x]['name'])))
    dfItems['campaign'] = (dfItems['campaign_id']
                           .apply(lambda x: dfCampaigns.loc[x]['description']))

    dfOrders = (dfItems[['campaign', 'client_name', 'quantity', 'final_price']]
                .groupby(['campaign', 'client_name'])
                .sum()
                .reset_index())

    statuses = (dfItems[['campaign', 'client_name', 'status']]
                .groupby(['campaign', 'client_name'])
                .agg(lambda x: set(x))
                .reset_index())

    dfOrders = dfOrders.merge(statuses, on=['campaign', 'client_name'])
    dfOrders = dfOrders.sort_values(['campaign', 'client_name'])
    print(dfOrders.to_string())
    dfOrders.to_csv('data/orders.csv', sep='\t', index=False)

def add_item():

    dfItem = pd.read_csv('data/items.csv', sep='\t').set_index('id')
    dfProducts = pd.read_csv('data/products.csv', sep='\t').set_index(['code', 'campaign_id'])
    dfCampaigns = pd.read_csv('data/campaigns.csv',sep='\t')
    dfClients = pd.read_csv('data/clients.csv', sep='\t').set_index('id')

    print(dfCampaigns[['id', 'description']].to_string(index=False))
    campaign_id = int(input('Campaign id:'))

    brand_id = int(dfCampaigns.loc[campaign_id]['brand_id'])

    insert = True
    while insert:
        i_id = len(dfItem)
        product_code = int(input('code:'))

        try:
            print(dfProducts.loc[(product_code, campaign_id)]['description'])
        except KeyError:
            print('{} Invalid code for campaign {}.'
                  .format(product_code,
                          (dfCampaigns
                           .set_index('id')
                           .loc[campaign_id]['description'])
                         )
                 )
            invalid_code = False
            while not invalid_code:
                product_code = int(input('code:'))
                try:
                    print(dfProducts.loc[(product_code, campaign_id)])
                    invalid_code = True

                except KeyError:
                    pass


        i_quantity = int(input('quantity:'))

        product_id = dfProducts.loc[(product_code, campaign_id), 'id']

        print(dfClients['name'].to_string())
        client_id = int(input('client id (-1 to new):'))

        if client_id == -1:
            client_id, dfClients = add_client()

        dfDiscounts = (pd.read_csv('data/discounts.csv', sep='\t')
                       .set_index(['client_id', 'brand_id']))

        ans = input('default discount: {}%. Apply? (yes: enter/no: any key)'
                    .format(str(dfDiscounts.loc[(client_id, brand_id), 'discount']*100)))

        if ans:
            i_discount = float(input('discount (0-1):'))
        else:
            i_discount = float(dfDiscounts.loc[(client_id, brand_id), 'discount'])

        cost_price = dfProducts.loc[(product_code, campaign_id), 'cost_price']

        if i_discount == 1:
            reg_sale_price = (dfProducts
                              .loc[(product_code, campaign_id), 'sale_price'])
            i_discount = 1-((cost_price)/(reg_sale_price))

        sale_price = (float(dfProducts
                            .loc[(product_code, campaign_id), 'sale_price'])
                      * (1-i_discount))

        profit = round(sale_price - cost_price, 2)
        while profit < 0:
            print('!!!Not applicable discount!!!', sale_price, cost_price, profit)
            i_discount = float(input('discount:'))
            sale_price = (float(dfProducts
                                .loc[[product_code, campaign_id]]['sale_price'])
                          * (1-i_discount))
            cost_price = dfProducts.loc[(product_code, campaign_id), 'cost_price']
            profit = round(sale_price - cost_price, 2)

        dfItem.loc[i_id]=[campaign_id, client_id, product_id,
                          i_discount, i_quantity, 'ordered']

        dfItem.to_csv('data/items.csv', sep='\t')

        ans = input('Insert new item? (yes: enter/no: any key)')
        if ans:
            insert=False

    update_orders()

def payable_report():
    dfItems = pd.read_csv('data/items.csv', sep='\t')
    dfClients = pd.read_csv('data/clients.csv', sep='\t').set_index('id')
    dfProducts = pd.read_csv('data/products.csv', sep='\t').set_index('id')
    dfCampaigns = pd.read_csv('data/campaigns.csv',sep='\t').set_index('id')

    dfItems['Produto'] = (dfItems['product_id']
                          .apply(lambda x: dfProducts.loc[x]['description']))
    dfItems['Valor'] = (dfItems['product_id']
                        .apply(lambda x: dfProducts.loc[x]['sale_price']))
    dfItems['Valor com desconto'] = round(dfItems['Valor'] *
                                          (1 - dfItems['discount']), 2)
    dfItems['Desconto'] = dfItems['discount'].copy()
    dfItems['Desconto'] = (round(dfItems['Desconto'], 2)*100).astype(str)+'%'
    dfItems['Quantidade'] = dfItems['quantity'].copy()

    for c_id in dfItems['client_id'].unique():
        dfC = dfItems[dfItems['client_id'] == c_id]
        totals = [0, 0]
        if any(dfC['status'] == 'delivered'):
            print('\n\033[1;37m{}\033[0;0m'.format(dfClients.loc[c_id]['name']))
            for campaign in dfC['campaign_id'].unique():
                total_c = [0, 0]

                dfPay = dfC[(dfC['campaign_id']==campaign) & (dfC['status']=='delivered')]
                if (len(dfPay) > 0):
                    print('\n\033[1;37m{}:\033[0;0m'
                          .format(dfCampaigns.loc[campaign]['description']))

                    if (any(dfPay['discount'])>0):
                        print((dfPay[['Produto', 'Quantidade', 'Valor',
                               'Desconto','Valor com desconto']]
                               .to_string(index=False,justify='left')))
                    else:
                        print((dfPay[['Produto', 'Quantidade', 'Valor']]
                               .to_string(index=False,justify='left')))
                    total_c[0] = (dfC[(dfC['campaign_id']==campaign) &
                                      (dfC['status']=='delivered')]['Valor'] *
                                 dfC[(dfC['campaign_id']==campaign) &
                                     (dfC['status']=='delivered')]['Quantidade']).sum()

                    total_c[1] = (dfC[(dfC['campaign_id']==campaign) &
                                      (dfC['status']=='delivered')]['Valor com desconto'] *
                                 dfC[(dfC['campaign_id']==campaign) &
                                     (dfC['status']=='delivered')]['Quantidade']).sum()

                    totals[0] += total_c[0]

                    totals[1] += total_c[1]

                    print('\033[1;37mTotal: {}\033[0;0m'.format(round(total_c[0],2)))
                    if total_c[0] != total_c[1]:
                        print('\033[1;37mTotal com desconto: {}\033[0;0m'
                              .format(round(total_c[1],2)))

            print('\n\033[1;37mTotal: {}\033[0;0m'.format(round(totals[0],2)))
            if totals[0] != totals[1]:
                print('\033[1;37mTotal com desconto: {}\033[0;0m'
                      .format(round(totals[1],2)))
            print('\n------------------------------------------------------------------------------------------------')

def update_status():
    dfItems = pd.read_csv('data/items.csv', sep='\t').set_index('id')

    status = ['to be ordered','ordered', 'received', 'delivered', 'paid']
    ans = 0
    while ((ans!= 1) & (ans != 2) & (ans != 3)):
        print('1 - By item')
        print('2 - By campaign')
        print('3 - By client')
        ans = int(input('option:'))

    if ans == 1:
        print(dfItems.to_string())
        i_id=-1
        while i_id not in dfItems.reset_index()['id'].unique():
            i_id = int(input('item id:'))
        actual_status = dfItems.loc[i_id]['status']
        next_status = status[status.index(actual_status)+1]
        chg = bool(input('Change from {} to {}? (yes: enter/no: any key)'
                         .format(actual_status, next_status)))

        if chg:
            for el in status:
                print('{}: {}'.format(status.index(el), el))
            next_status = status[int(input('new status id:'))]
            dfItems.loc[i_id, 'status'] = next_status
        else:
            dfItems.loc[i_id,'status'] = next_status

    elif ans == 2:
        dfCampaigns = pd.read_csv('data/campaigns.csv', sep='\t').set_index('id')
        print(dfCampaigns[['description', 'catalog_request_date',
                           'catalog_delivery_date']].to_string())
        c_id=-1
        while c_id not in dfCampaigns.reset_index()['id'].unique():
            c_id = int(input('campaign id:'))

        ans = 0
        while ((ans!= 1) & (ans != 2)):
            print('1 - All campaign')
            print('2 - By client')
            ans = int(input('update:'))

        if ans == 1:
            for el in status:
                print('{}: {}'.format(status.index(el), el))
            next_status = status[int(input('new status id:'))]
            dfItems.loc[dfItems['campaign_id'] == c_id, 'status'] = next_status
        else:
            dfCamp = dfItems[dfItems['campaign_id'] == c_id]
            dfClients = pd.read_csv('data/clients.csv', sep='\t')

            print(dfClients[dfClients['id']
                            .apply(lambda x: True if x in dfCamp['client_id'].unique() else False)]
                  ['name'].to_string())
            client_id=-1
            while client_id not in dfCamp['client_id'].unique():
                client_id = int(input('client id:'))

#             for client_id in dfCamp['client_id'].unique():
#                 print(dfClients.loc[client_id]['name'])
            for el in status:
                print('{}: {}'.format(status.index(el), el))
            next_status = status[int(input('new status id:'))]
            dfItems.loc[(dfItems['campaign_id'] == c_id) &
                        (dfItems['client_id'] == client_id), 'status'] = next_status

    elif ans == 3:
        dfClients = pd.read_csv('data/clients.csv', sep='\t').set_index('id')
        print(dfClients['name'].to_string())
        c_id=-1
        while c_id not in dfClients.reset_index()['id'].unique():
            c_id = int(input('client id:'))

        for el in status:
            print('{}: {}'.format(status.index(el), el))
        next_status = status[int(input('new status id:'))]
        dfItems.loc[dfItems['client_id'] == c_id, 'status'] = next_status

    dfItems.to_csv('data/items.csv', sep='\t')
    update_orders()


def pdf_payable_report():
    dfItems = pd.read_csv('data/items.csv', sep='\t')
    dfClients = pd.read_csv('data/clients.csv', sep='\t').set_index('id')
    dfProducts = pd.read_csv('data/products.csv', sep='\t').set_index('id')
    dfCampaigns = pd.read_csv('data/campaigns.csv',sep='\t').set_index('id')

    dfItems['Produto'] = (dfItems['product_id']
                          .apply(lambda x: dfProducts.loc[x]['description']))
    dfItems['Valor'] = (dfItems['product_id']
                        .apply(lambda x: dfProducts.loc[x]['sale_price']))
    dfItems['Valor com desconto'] = round(dfItems['Valor'] *
                                          (1 - dfItems['discount']), 2)
    dfItems['Desconto'] = dfItems['discount'].copy()
    dfItems['Desconto'] = (round(dfItems['Desconto'], 2)*100).astype(str)+'%'
    dfItems['Quantidade'] = dfItems['quantity'].copy()

    styleSheet = getSampleStyleSheet()
    doc = SimpleDocTemplate("reports/{}_Débitos.pdf".format(datetime.today().date()))
    doc.pagesize = landscape(A4)
    elements = []

    for c_id in dfItems['client_id'].unique():
        dfC = dfItems[dfItems['client_id'] == c_id]
        if any(dfC['status'] == 'delivered'):
            totals = [0, 0]
            TxtClient = Paragraph('''<b>{}</b>'''
                                  .format(dfClients.loc[c_id]['name']),
                                  styleSheet["BodyText"])
            elements.append(TxtClient)

            for campaign in dfC['campaign_id'].unique():

                dfPay = dfC[(dfC['campaign_id']==campaign) & (dfC['status']=='delivered')]

                if(len(dfPay)>0):

                    TxtCampaign = Paragraph('''<b>{}</b>'''
                                            .format((dfCampaigns.loc[campaign]['description'])),
                                            styleSheet["BodyText"])
                    elements.append(TxtCampaign)


                    if (any(dfPay['discount'])>0):
                        dfPay = dfPay[['Produto', 'Quantidade', 'Valor',
                                       'Desconto','Valor com desconto']]
                        header = dfPay.columns.tolist()
                        header = [Paragraph('''<b>{}</b>'''.format(c),
                                            styleSheet["BodyText"]) for c in header]
                        footer = ['TOTAL', '-', round(sum(dfPay['Valor']*dfPay['Quantidade']),2), '-',
                                    round(sum(dfPay['Valor com desconto']*dfPay['Quantidade']),2)]
                        data= [header] + round(dfPay,2).astype(str).values.tolist() + [footer]
                        t=Table(data)

                        data_len = len(data)
                        for each in range(data_len):
                            if each % 2 == 0:
                                bg_color = colors.whitesmoke
                            else:
                                bg_color = colors.lavender

                            t.setStyle(TableStyle([('BACKGROUND', (0, each),
                                                   (-1, each), bg_color)]))

                        t.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                                               ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                               ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
                        elements.append(t)

                    else:
                        dfPay = dfPay[['Produto', 'Quantidade', 'Valor']]
                        header = dfPay.columns.tolist()
                        header = [Paragraph('''<b>{}</b>'''.format(c),
                                            styleSheet["BodyText"]) for c in header]

                        footer = ['TOTAL', '-', round(sum(dfPay['Valor']),2)]

                        data= [header] + round(dfPay,2).astype(str).values.tolist() + [footer]
                        t=Table(data)

                        data_len = len(data)
                        for each in range(data_len):
                            if each % 2 == 0:
                                bg_color = colors.whitesmoke
                            else:
                                bg_color = colors.lavender

                            t.setStyle(TableStyle([('BACKGROUND', (0, each),
                                                   (-1, each), bg_color)]))

                        t.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                                               ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                               ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
                        elements.append(t)

                    totals[0] += (dfC[(dfC['campaign_id']==campaign) & (dfC['status']=='delivered')]['Valor'] *
                                 dfC[(dfC['campaign_id']==campaign) & (dfC['status']=='delivered')]['Quantidade']).sum()
                    totals[1] += (dfC[(dfC['campaign_id']==campaign) & (dfC['status']=='delivered')]['Valor com desconto'] *
                                 dfC[(dfC['campaign_id']==campaign) & (dfC['status']=='delivered')]['Quantidade']).sum()

            TxtTotals0 = Paragraph('''<b>Total: R${}</b>'''.format(round(totals[0],2)), styleSheet["BodyText"])
            elements.append(TxtTotals0)

            if totals[0] != totals[1]:
                TxtTotals1 = Paragraph('''<b>Total com Desconto: R${}</b>'''.format(round(totals[1],2)), styleSheet["BodyText"])
                elements.append(TxtTotals1)
            newLine = Paragraph('''<br />''', styleSheet["BodyText"])
            elements.append(newLine)

            line = MCLine(500)
            elements.append(line)
    doc.build(elements)

def pdf_delivery_report():
    dfItems = pd.read_csv('data/items.csv', sep='\t')
    dfClients = pd.read_csv('data/clients.csv', sep='\t').set_index('id')
    dfProducts = pd.read_csv('data/products.csv', sep='\t').set_index('id')
    dfCampaigns = pd.read_csv('data/campaigns.csv',sep='\t').set_index('id')

    dfItems['Produto'] = (dfItems['product_id']
                          .apply(lambda x: dfProducts.loc[x]['description']))
    dfItems['Valor'] = (dfItems['product_id']
                        .apply(lambda x: dfProducts.loc[x]['sale_price']))
    dfItems['Valor com desconto'] = round(dfItems['Valor'] *
                                          (1 - dfItems['discount']), 2)
    dfItems['Desconto'] = dfItems['discount'].copy()
    dfItems['Desconto'] = (round(dfItems['Desconto'], 2)*100).astype(str)+'%'
    dfItems['Quantidade'] = dfItems['quantity'].copy()

    styleSheet = getSampleStyleSheet()

    for campaign_id in dfCampaigns.reset_index()['id'].unique():
        doc = SimpleDocTemplate("reports/{}.pdf".format((dfCampaigns.loc[campaign_id]['description'])
                                                        .strip(' ')
                                                        .replace('/','_')))
        doc.pagesize = landscape(A4)
        elements = []

        TxtCampaign = Paragraph('''<br /><b>{}</b>'''
                                .format((dfCampaigns.loc[campaign_id]['description'])),
                                styleSheet["Heading1"])
        elements.append(TxtCampaign)

        dfC = dfItems[dfItems['campaign_id'] == campaign_id]

        totals = [0, 0]

        for c_id in dfC['client_id'].unique():
            doc1 = SimpleDocTemplate("reports/{}_{}.pdf".format(dfClients.loc[c_id]['name'],
                                                                (dfCampaigns.loc[campaign_id]['description'])
                                                                .strip(' ')
                                                                .replace('/','_')))
            doc1.pagesize = landscape(A4)
            elements1 = []

            elements1.append(TxtCampaign)

            dfClient = dfC[dfC['client_id'] == c_id]


            TxtClient = Paragraph('''<b>{}</b>'''
                                  .format(dfClients.loc[c_id]['name']),
                                  styleSheet["BodyText"])
            elements.append(TxtClient)
            elements1.append(TxtClient)

            if (any(dfClient['discount'])>0):
                header = dfClient[['Produto', 'Quantidade', 'Valor',
                                       'Desconto','Valor com desconto']].columns.tolist()
                header = [Paragraph('''<b>{}</b>'''.format(c),
                                    styleSheet["BodyText"]) for c in header]
                footer = ['TOTAL', '-', round(sum(dfClient['Valor']*dfClient['Quantidade']),2), '-',
                            round(sum(dfClient['Valor com desconto']*dfClient['Quantidade']),2)]

                data= [header] + round(dfClient[['Produto', 'Quantidade', 'Valor',
                                       'Desconto','Valor com desconto']],2).astype(str).values.tolist() + [footer]
            else:
                header = dfClient[['Produto', 'Quantidade', 'Valor']].columns.tolist()
                header = [Paragraph('''<b>{}</b>'''.format(c),
                                    styleSheet["BodyText"]) for c in header]

                footer = ['TOTAL', '-', round(sum(dfClient['Valor']),2)]

                data= [header] + round(dfClient[['Produto', 'Quantidade', 'Valor']],2).astype(str).values.tolist() + [footer]

            t=Table(data)

            data_len = len(data)
            for each in range(data_len):
                if each % 2 == 0:
                    bg_color = colors.whitesmoke
                else:
                    bg_color = colors.lavender

                t.setStyle(TableStyle([('BACKGROUND', (0, each),
                                       (-1, each), bg_color)]))
            t.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                                   ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                   ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
            elements.append(t)
            elements1.append(t)

            totals[0] += (dfClient['Valor'] * dfClient['Quantidade']).sum()

            totals[1] += (dfClient['Valor com desconto'] * dfClient['Quantidade']).sum()

            doc1.build(elements1)

        TxtTotals0 = Paragraph('''<b>Total: R${}</b>'''.format(round(totals[0],2)), styleSheet["BodyText"])
        elements.append(TxtTotals0)

        TxtTotals1 = Paragraph('''<b>Total com Desconto: R${}</b>'''.format(round(totals[1],2)), styleSheet["BodyText"])
        elements.append(TxtTotals1)

        TxtLucro = Paragraph('''<b>Lucro: R${}</b>'''.format(round((totals[0]-totals[1]),2)), styleSheet["BodyText"])
        elements.append(TxtLucro)
        newLine = Paragraph('''<br />''', styleSheet["BodyText"])
        elements.append(newLine)

        line = MCLine(500)
        elements.append(line)
        doc.build(elements)


def display():
    while True:
        print('\n Menu:')
        print('1 - Add new product')
        print('2 - Add new client')
        print('3 - Add new item')
        print('4 - Update item status')
        print('5 - Add new campaign')
        print('6 - Add new revendor (in progress)')
        print('7 - Show orders report')
        print('8 - Show payable report and generate PDF')
        print('9 - Generate PDF delivery report')
        print('0 - Finish')
        op = int(input('Option:'))
        if op == 0:
            break;
        elif op == 1:
            add_product()
        elif op == 2:
            add_client()
        elif op == 3:
            add_item()
        elif op == 4:
            update_status()
        elif op == 5:
            add_campaign()
#         elif op == 6:
#             add_revendor()
        elif op == 7:
            update_orders()
        elif op == 8:
            pdf_payable_report()
            payable_report()
        elif op == 9:
            pdf_delivery_report()
        else:
            print('\n !!! Invalid option !!!')
