# Hand-Tracking-Using-Opencv

## About The Project

This Python project utilizes OpenCV and MediaPipe to perform real-time hand tracking using a webcam. The original script captures video input from the default camera, processes the frames to detect and track hand landmarks using the MediaPipe Hands module, and subsequently visualizes the landmarks on the live feed.

### 🏎️ NEW: Interactive Racing Hand Game

The project now includes an **Interactive Racing Game** that combines hand gesture recognition with real-time racing gameplay! Control a race car using intuitive hand gestures and navigate through obstacles on a racing track.

#### 🎮 Game Features:
- **Speed Control**: Use finger gap on your left hand (right in camera due to mirroring) to control acceleration and braking
- **Steering Control**: Use your right hand (left in camera) vertical position to steer left and right
- **Dynamic Obstacles**: Randomly generated obstacles that you must avoid
- **Real-time Scoring**: Score points by avoiding obstacles and maintaining speed
- **Collision Detection**: Realistic collision system that affects your car's performance
- **Racing UI**: Live speed, score, and time display

#### 🕹️ Game Controls:
- 🚗 **Speed Control (Left Hand - appears as right in camera)**:
  - **Small gap** between thumb and index finger: **BRAKE** 🛑
  - **Large gap** between thumb and index finger: **ACCELERATE** 🚀
  - **Medium gap**: **Coast/Maintain Speed** ⚡
- 🎯 **Steering Control (Right Hand - appears as left in camera)**:
  - **Move hand UP**: **Turn LEFT** ⬅️
  - **Move hand DOWN**: **Turn RIGHT** ➡️
  - **Center position**: **Go STRAIGHT** ⬆️

#### 🏆 Objective:
Navigate your race car through the track, avoid orange obstacles, stay within the white track boundaries, and achieve the highest score possible!

https://github.com/KalyanMurapaka45/Hand-Tracking-Using-Opencv/assets/101493756/e0d7fae9-4a16-4639-b5fe-04d5c7f6ce38


## Built With

 - OpenCV
 - MediaPipe
 - NumPy
 - Matplotlib
 - Pygame (for advanced 3D visualization)
   

## Available Applications

### 1. Basic Hand Tracking (`app.py`)
- Real-time hand landmark detection
- FPS display
- Basic hand tracking visualization

### 2. Media Hand Tracking (`Hand Tracking from Media .py`)
- Process video files for hand tracking
- Save output videos with hand tracking overlays

### 3. � Interactive Racing Game (`racing_hand_game.py`) - **FEATURED**
- **Real-time racing gameplay** controlled entirely by hand gestures
- **Speed control** using finger gap spacing
- **Steering control** using hand position
- **Dynamic obstacle avoidance** with collision detection
- **Live scoring system** and racing UI
- **Camera mirroring awareness** for intuitive controls
   

## Getting Started

This will help you understand how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

## Installation Steps

### Option 1: Installation from GitHub

Follow these steps to install and set up the project directly from the GitHub repository:

1. **Clone the Repository**
   - Open your terminal or command prompt.
   - Navigate to the directory where you want to install the project.
   - Run the following command to clone the GitHub repository:
     ```
     git clone https://github.com/KalyanMurapaka45/Hand-Tracking-Using-Opencv.git
     ```

2. **Create a Virtual Environment** (Optional but recommended)
   - It's a good practice to create a virtual environment to manage project dependencies. Run the following command:
     ```
     conda create -p <Environment_Name> python==<python version> -y
     ```

3. **Activate the Virtual Environment** (Optional)
   - Activate the virtual environment based on your operating system:
       ```
       conda activate <Environment_Name>/
       ```

4. **Install Dependencies**
   - Navigate to the project directory:
     ```
     cd [project_directory]
     ```
   - Run the following command to install project dependencies:
     ```
     pip install -r requirements.txt
     ```

5. **Run the Project**
   - For basic hand tracking:
     ```
     python app.py
     ```
   - **For the interactive racing game (RECOMMENDED):**
     ```
     python racing_hand_game.py
     ```
   - For motorsport engine visualization:
     ```
     python motorsport_hand_tracker_simple.py
     ```
   - For advanced engine visualization:
     ```
     python motorsport_hand_tracker.py
     ```

6. **Access the Project**
   - Open a web browser or the appropriate client to access the project.
  

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.


## Contact

Hema Kalyan Murapaka - [@kalyanmurapaka274@gmail.com](kalyanmurapaka274@gmail.com)


## Acknowledgements

We'd like to extend our gratitude to all individuals and organizations who have played a role in the development and success of this project. Your support, whether through contributions, inspiration, or encouragement, has been invaluable. Thank you for being a part of our journey.
