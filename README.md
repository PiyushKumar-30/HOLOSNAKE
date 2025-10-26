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






