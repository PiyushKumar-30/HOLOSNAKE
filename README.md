# 🕹️ HOLOSNAKE: An Augmented Reality Gesture Game

**HOLOSNAKE** is an interactive **Augmented Reality-based Snake Game** that uses **real-time hand gesture tracking** to control gameplay — no keyboard or mouse required!  
Built using **Python**, **OpenCV**, **cvzone**, and **pygame**, this project blends **computer vision** and **game development** into an engaging experience.

---

## 🚀 Features

- 🎮 **Gesture-based Control:** Play the snake game using your hand movements via webcam.  
- 👋 **Real-time Hand Tracking:** Uses `cvzone.HandTrackingModule` to detect and track hand gestures.  
- 🔊 **Interactive Menu:** Includes music, sound effects, and animated transitions.  
- 🌈 **Multiple Levels:** Select from different levels for increasing difficulty.  
- 🧱 **Dynamic Obstacles:** Real-time collision detection with walls and self-body.  
- 🕵️ **Modern UI:** Minimalistic design with smooth gameplay experience.

---
# Game Images
<img width="602" height="340" alt="image" src="https://github.com/user-attachments/assets/26dd9e52-72b0-48ce-ba7a-da9f22ae8e76" />
<img width="602" height="340" alt="image" src="https://github.com/user-attachments/assets/3e530877-cba7-4c11-a912-716bd945a162" />
<img width="602" height="338" alt="image" src="https://github.com/user-attachments/assets/b9dd5d3e-3561-49b0-8cc9-17307ca3dd2e" />




---

## 🛠️ Tech Stack

| Component | Technology |
|------------|-------------|
| Programming Language | Python |
| Computer Vision | OpenCV, cvzone |
| Game Engine | pygame |
| Other Libraries | numpy |

---

## 🧩 Project Structure
   ```bash
   HOLOSNAKE/
   │
   ├── main.py                  # Main game code
   ├── requirements.txt         # Python dependencies
   ├── README.md                # Project description
   │
   ├── Game Music/              # All music and sound files
   │   ├── background.wav
   │   ├── eat.wav
   │   ├── game_over.wav
   │   ├── menu_hover.mp3
   │   └── menu_select.wav
   │
   ├── Games Images/            # Images used in the game
   │   ├── donut.png            # Food image
   │   └── wall.png             # Wall/obstacle image
   ├── Game Code Files
       ├── highscore.json           # Stores high score

   ```


---

## ⚙️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/HOLOSNAKE.git
   cd HOLOSNAKE
2. **Install Dependencies**
   ```bash
    pip install -r requirements.txt
3. **Run the Game**
   ```bash
   python main.py
   ```






