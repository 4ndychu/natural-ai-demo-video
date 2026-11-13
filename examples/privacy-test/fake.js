// Fake data for NAVI's privacy test (Phase 4). None of it is real. Keys are stored in pieces so secret scanners
// don't mistake this file for a leak; scripts/privacy/test_privacy.py joins them the same way.
window.FAKE = {
  "blur": {
    "account_name": "Jane Cooper",
    "emails": ["jane.doe@northwind-mail.com", "m.ross@harbourline.io", "li.wei@quillmail.net", "a.osei@fernbank.co"],
    "typed_email": "sam.reyes@kestrelpost.com",
    "phones": ["+44 20 7946 0958", "(415) 555-0132"],
    "addresses": ["221 Baker Street", "SW1A 1AA"],
    "customer_names": ["Marcus Ross", "Li Wei", "Ama Osei"],
    "money": ["$12,480.00", "£3,200", "$1,029.50"],
    "counts": ["1,204 customers", "18.2k followers"],
    "keys": [["sk", "live", "4eC39HqLyjWDarjtT1zdp7dc"], ["ghp", "R8kLm2Qx7vN4pT9wZ3cY6bH1jF5dS0aE8uGt"], ["AKIA", "IOSFODNN7EXAMPLQ"]],
    "card": ["4242", "4242", "4242", "4242"],
    "masked_card": "•••• 4242",
    "codes": ["k3d9-x7p2-m4q8", "h6w2-r9t5-c8n1"],
    "gov_id": "123-45-6789",
    "login_link": ["https://app.acme.test/login?token=", "Zx81kQ0pLm4Nb7Vt2Rc9Yh"],
    "hide_word": "Northwind",
    "in_image": ["m.ross@harbourline.io", "$4,310.00"]
  },
  "show": ["Acme Dashboard", "Customers", "API keys", "Pro $29/month", "48,210 tokens used", "8 Nov 2026", "Reveal key", "Invite a teammate"]
};
window.FAKE.join = {
  key: (k) => (k[0] === "AKIA" ? k.join("") : k.join("_")),
  card: (c) => c.join(" "),
  link: (l) => l.join(""),
};
