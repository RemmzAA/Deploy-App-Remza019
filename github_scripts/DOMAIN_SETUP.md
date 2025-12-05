# 🚀 019solutions.com - DOMAIN & DNS SETUP GUIDE

## 📋 TRENUTNO STANJE (Baziran na Namecheap skrinovima):

✅ **Domen je aktivan** (Jul 28, 2025 - Jul 28, 2026)
✅ **PremiumDNS je konfigurisan**
✅ **Email hosting aktivan** (Private Email sa 1 mailbox)
⚠️ **DNS pokazuje na parking page**

## 🔧 DNS KONFIGURACIJA - KORAK PO KORAK:

### **Korak 1: UKLONITI postojeće records**
U **Advanced DNS** sekciji uklonite:
```
❌ DELETE: CNAME Record | www | parkingpage.namecheap.com
❌ DELETE: URL Redirect Record | @ | http://www.019solutions.com/
```

### **Korak 2: DODATI nove A records**
```
✅ ADD: A Record | @ | [IP_ADRESA_HOSTINGA] | TTL: Automatic
✅ ADD: A Record | www | [IP_ADRESA_HOSTINGA] | TTL: Automatic
```

### **Korak 3: ZADRŽATI postojeće email records**
```
✅ KEEP: TXT Record | @ | v=spf1 include:spf.efwd.registrar-servers.com ~all
```

## 📧 EMAIL KONFIGURACIJA

### Postojeći email setup:
```
✅ contact@019solutions.com (Private Email - 1 mailbox aktivan)
✅ Email Forwarding: Konfigurisano u Mail Settings
```

### Dodati novi email forwarder:
```
Dodaj: info@019solutions.com -> risticvladica@hotmail.com
```

## 🌐 HOSTING OPCIJE

### **Opcija 1: Namecheap Hosting**
```bash
1. Idi na "Hosting List" u dashboard
2. Kupi Shared Hosting paket
3. Upload files u public_html/
4. A Record automatski se podesi na Namecheap IP
```

### **Opcija 2: Eksterni hosting**
```bash
1. Kupi hosting kod bilo kog provider-a (DigitalOcean, AWS, itd.)
2. Dobij IP adresu
3. Dodaj A records sa tim IP-om
4. Upload website files
```

## 📞 KONTAKT INFORMACIJE AŽURIRANE:

```
📧 Business: contact@019solutions.com
📧 Direct: risticvladica@hotmail.com  
📞 Phone: +41 78 766 41 81 (Switzerland)
💬 WhatsApp: https://wa.me/41787664181
💬 Viber: viber://chat?number=41787664181
🌐 Website: www.019solutions.com
📍 Location: Switzerland
```

## ⚡ GO-LIVE CHECKLIST

- [ ] Kupi/konfiguriši hosting server
- [ ] Dobij IP adresu hostinga  
- [ ] Ukloni parking page DNS records
- [ ] Dodaj A records sa novom IP adresom
- [ ] Upload website files
- [ ] Test email: contact@019solutions.com
- [ ] Test website: www.019solutions.com
- [ ] Test WhatsApp/Viber linkove
- [ ] SSL certificate (Let's Encrypt)

## 🚨 NAPOMENE:

1. **DNS propagacija** može da traje **24-48 sati**
2. **Private Email** već radi - testiraj contact@019solutions.com
3. **WhatsApp/Viber** linkovi rade odmah
4. **Swiss phone number** (+41) dodaje međunarodnu legitimnost

---

🎯 **READY FOR LAUNCH!**  
Contact: contact@019solutions.com | +41 78 766 41 81  
Website: www.019solutions.com

© 2025 019 Solutions - All Rights Reserved