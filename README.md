Here’s a **README.md** file for your GitHub repository:  

---

### **🚀 Telegram Bot (Railway Deployment)**
A simple Telegram bot deployed on **Railway.app** that supports **deep linking** and sends **messages & images**.

---

## **📌 Features**
✅ Supports **deep linking** (`/start mvs100`, `/start deepseek`)  
✅ Sends **text messages & images**  
✅ **No auto-delete** (messages stay permanently)  
✅ Runs **24/7 on Railway** using **polling**  

---

## **🛠 Setup & Deployment**
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### **2️⃣ Set Up Railway**
1. Go to **[Railway.app](https://railway.app/)** and create an account.  
2. Click **"New Project" → "Deploy from GitHub"**.  
3. Select your **GitHub repository**.  

### **3️⃣ Add Environment Variables**
- In **Railway Dashboard** → Go to **"Variables"** and add:  
  ```
  BOT_TOKEN=your_telegram_bot_token
  MVS100_MESSAGE=Your message for mvs100
  ```

### **4️⃣ Deploy**
Click **"Deploy"** on Railway, and your bot will start running! 🎉  

---

## **💻 Running Locally**
If you want to run the bot on your own PC:  
1️⃣ Install dependencies:
```sh
pip install python-telegram-bot flask
```
2️⃣ Run the bot:
```sh
python main.py
```

---

## **⚡ How to Use**
💡 **Start the bot by clicking this link:**  
```
https://t.me/YourBotUsername?start=mvs100
```

| Command         | Action                        |
|----------------|-----------------------------|
| `/start mvs100`  | Sends a message for MVS100  |
| `/start mvs200`  | Sends a message for MVS200  |
| `/start deepseek` | Sends text + an image      |

---

## **📝 License**
This project is **open-source**. Feel free to modify & improve! 🚀  

---

### ✅ **Now, just replace `yourusername/your-repo` and `YourBotUsername` before uploading!**  
Let me know if you need changes! 🚀
