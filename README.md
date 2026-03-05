# 🐉 Dragon Animation

A mesmerizing interactive dragon animation built with Python's built-in `tkinter` library. Move your mouse across the window and watch the dragon glide, flap its wings, and breathe fire — all in real time.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=flat-square&logo=python)
![Tkinter](https://img.shields.io/badge/Library-tkinter-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![No Install](https://img.shields.io/badge/Dependencies-none-brightgreen?style=flat-square)

---

## ✨ Features

- 🐉 **34-segment dragon body** that smoothly snakes and follows your mouse cursor
- 🪶 **Flapping bat wings** with 4 finger bones and membrane veins, animated in real time
- 🔥 **Fire breath** — particle stream shoots from the mouth as the dragon moves
- 👁️ **Glowing cyan eyes** with pulsing halos and magical eye sparks
- ⚡ **Energy trail** drifting off the tail tip
- 🌌 **Twinkling starfield** with 220 stars and nebula atmosphere blobs
- 🔱 **Animated spine spikes** that pulse along the back
- 🎨 **Dark navy palette** — moody, cinematic, and restrained
- 🚀 **~60 FPS** smooth animation using tkinter's canvas

---

## 🚀 Getting Started

### Requirements

- Python **3.7 or higher**
- No external libraries needed — uses only Python's built-in `tkinter`

### Run it

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/dragon-animation.git

# Go into the folder
cd dragon-animation

# Run the animation
python dragon_animation.py
```

> **VS Code users:** just open the file and press `F5`, or right-click → *Run Python File in Terminal*.

---

## 🎮 Controls

| Action | Effect |
|--------|--------|
| Move mouse | Dragon follows your cursor |
| Close window | Exit the animation |

---

## 🗂️ Project Structure

```
dragon-animation/
│
├── dragon_animation.py   # Main animation file (all code in one place)
└── README.md             # You're reading this!
```

---

## 🧠 How It Works

| System | Description |
|--------|-------------|
| **Inverse Kinematics** | Each body segment is pulled toward the one in front of it, creating the fluid snake-like motion |
| **Ribbon Rendering** | The body is drawn as a smooth polygon by offsetting left/right edges from a centreline spine |
| **Particle Pool** | 200 particles are pre-created and recycled to avoid creating/destroying objects every frame |
| **Wing Physics** | Wing finger tips are offset using a sine-wave flap angle that updates each frame |
| **Star Twinkle** | Each star has a unique speed and phase offset so they all pulse independently |

---

## 📸 Preview

> Move your mouse — the dragon follows!

```
🌌  Starfield background
🐉  Dragon chases cursor
🔥  Fire breath from mouth
⚡  Glowing tail trail
✨  Eye sparks float away
🪶  Wings flap rhythmically
```

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🙌 Author

Made with Python & creativity.  
Feel free to fork, star ⭐, and make it your own!
