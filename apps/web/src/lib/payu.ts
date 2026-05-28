import crypto from "crypto";

// PayU hosted-checkout helper.
// Docs: hash = sha512(key|txnid|amount|productinfo|firstname|email|udf1..udf5||||||SALT)
const PAYU_BASE: Record<string, string> = {
  test: "https://test.payu.in/_payment",
  production: "https://secure.payu.in/_payment",
};

export function payuConfig() {
  const key = process.env.PAYU_MERCHANT_KEY;
  const salt = process.env.PAYU_SALT;
  const env = (process.env.PAYU_ENV || "test").toLowerCase();
  if (!key || !salt) throw new Error("PAYU_MERCHANT_KEY / PAYU_SALT not set");
  return { key, salt, env, action: PAYU_BASE[env] || PAYU_BASE.test };
}

type PayuRequest = {
  txnid: string;
  amount: string; // rupees with 2 decimals, e.g. "999.00"
  productinfo: string;
  firstname: string;
  email: string;
  phone: string;
  surl: string; // success URL
  furl: string; // failure URL
  udf1?: string; // we pass order_id here
};

export function buildPayuForm(req: PayuRequest) {
  const { key, salt, action } = payuConfig();
  const udf1 = req.udf1 || "";
  // hash sequence: key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5||||||salt
  const hashString = [
    key, req.txnid, req.amount, req.productinfo, req.firstname, req.email,
    udf1, "", "", "", "", "", "", "", "", "", salt,
  ].join("|");
  const hash = crypto.createHash("sha512").update(hashString).digest("hex");
  return {
    action,
    fields: {
      key,
      txnid: req.txnid,
      amount: req.amount,
      productinfo: req.productinfo,
      firstname: req.firstname,
      email: req.email,
      phone: req.phone,
      surl: req.surl,
      furl: req.furl,
      udf1,
      hash,
    },
  };
}

// Verify the response hash PayU posts back to surl/furl.
// reverse sequence: salt|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key
export function verifyPayuResponse(p: Record<string, string>): boolean {
  const { key, salt } = payuConfig();
  const seq = [
    salt, p.status, "", "", "", "", "", "",
    p.udf5 || "", p.udf4 || "", p.udf3 || "", p.udf2 || "", p.udf1 || "",
    p.email, p.firstname, p.productinfo, p.amount, p.txnid, key,
  ].join("|");
  const expected = crypto.createHash("sha512").update(seq).digest("hex");
  return expected === p.hash;
}
