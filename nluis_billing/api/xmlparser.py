from django.conf import settings
from xml.sax.saxutils import escape


def billxml(bill):
    spCode = settings.SP_CODE
    subSp = settings.SUB_SP
    systemId = settings.SYSTEM_ID
    itemsxml = ''
    issuedDate = (bill.expiry_date).strftime(settings.BILL_DATE_INPUT_FORMATS)
    expDate = (bill.issued_date).strftime(settings.BILL_DATE_INPUT_FORMATS)
    phone = str(bill.holder_phone)
    phone = phone.replace(" ", "")
    phone = phone.replace("+", "")

    for item in bill.items():
        itemsxml = f'''
            <BillItem>
                <BillItemRef>{item.id}</BillItemRef>
                <UseItemRefOnPay>N</UseItemRefOnPay>
                <BillItemAmt>{item.amount}</BillItemAmt>
                <BillItemEqvAmt>{item.eqvAmount()}</BillItemEqvAmt>
                <BillItemMiscAmt>0.0</BillItemMiscAmt>
                <GfsCode>{item.fee.gfs_code}</GfsCode>
            </BillItem>
            '''

    content = f'''
        <gepgBillSubReq>
        <BillHdr>
        <SpCode> {spCode}</SpCode>
        <RtrRespFlg>true</RtrRespFlg>
        </BillHdr>
        <BillTrxInf>
        <BillId>NLUIS-{bill.id}</BillId>
        <SubSpCode> {subSp} </SubSpCode>
        <SpSysId> {systemId} </SpSysId>
        <BillAmt> {bill.totalAmount()} </BillAmt>
        <MiscAmt>0.0</MiscAmt>
        <BillExprDt> {expDate} </BillExprDt>
        <PyrId> {escape(bill.holder_name)} </PyrId>
        <PyrName> {escape(bill.holder_name)} </PyrName>
        <BillDesc>  </BillDesc>
        <BillGenDt> {issuedDate} </BillGenDt>
        <BillGenBy> {escape(bill.holder_name)} </BillGenBy>
        <BillApprBy> {escape(bill.holder_name)}</BillApprBy>
        <PyrCellNum>{phone}</PyrCellNum>" 
        <PyrEmail/>
        <Ccy>{bill.currency.code}</Ccy>
        <BillEqvAmt>{bill.totalEqvAmount()}</BillEqvAmt>
        <RemFlag>true</RemFlag>
        <BillPayOpt> {bill.paymentOption()}</BillPayOpt>
        <BillItems>
         {itemsxml} 
        </BillItems>
        </BillTrxInf>
        </gepgBillSubReq>'''

    return content
