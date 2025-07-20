import cv2
import mediapipe as mp
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import math
import random
from typing import Optional, Tuple, List
import threading

class RacingGame:
    """Interactive racing game controlled by hand gestures"""
    
    def __init__(self):
        # Set up the figure and axis for fullscreen
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.patch.set_facecolor('black')
        
        # Make it fullscreen
        mng = plt.get_current_fig_manager()
        try:
            mng.window.state('zoomed')  # Windows
        except:
            try:
                mng.resize(*mng.window.maxsize())  # Alternative
            except:
                pass  # Fallback to regular size
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('darkgreen')
        
        # Game state
        self.car_x = 5.0  # Car X position (center of track)
        self.car_y = 1.0  # Car Y position
        self.car_speed = 0.0  # Current speed
        self.max_speed = 0.3
        self.steering_angle = 0.0
        
        # Track parameters
        self.track_width = 3.0
        self.track_center_x = 5.0
        self.track_left = self.track_center_x - self.track_width / 2
        self.track_right = self.track_center_x + self.track_width / 2
        
        # Game elements
        self.obstacles = []
        self.checkpoint_y = 0
        self.score = 0
        self.game_over = False
        self.lap_time = 0
        self.start_time = time.time()
        self.collision_slowdown = 1.0  # Multiplier for speed after collision
        
        # Visual elements
        self.car_color = 'red'
        self.track_color = 'gray'
        self.obstacle_color = 'orange'
        
        # Keyboard state for game control
        self.key_pressed = None
        
        # Generate initial obstacles
        self.generate_obstacles()
        
        # Connect keyboard events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        plt.ion()  # Interactive mode
        
    def generate_obstacles(self):
        """Generate random obstacles on the track"""
        self.obstacles.clear()
        for i in range(5):
            # Random position across track width
            obstacle_x = random.uniform(self.track_left + 0.3, self.track_right - 0.3)
            obstacle_y = 3 + i * 2  # Spaced out vertically
            self.obstacles.append({'x': obstacle_x, 'y': obstacle_y, 'hit': False})
    
    def update_car_position(self, left_hand_distance, right_hand_distance, left_hand_y, right_hand_y):
        """Update car position based on hand gestures"""
        
        # Speed control: gap between fingers on left hand (appears as right due to mirror)
        if left_hand_distance is not None:
            # Small gap = slow/brake, large gap = accelerate
            if left_hand_distance < 0.05:  # Very small gap - brake
                self.car_speed = max(0, self.car_speed - 0.02)
            elif left_hand_distance > 0.15:  # Large gap - accelerate
                target_speed = self.max_speed * self.collision_slowdown
                self.car_speed = min(target_speed, self.car_speed + 0.015)
            else:  # Medium gap - maintain speed
                self.car_speed = max(0, self.car_speed - 0.005)  # Slight deceleration
        else:
            # No speed control hand detected - gradual slowdown
            self.car_speed = max(0, self.car_speed - 0.008)
        
        # Gradually recover from collision slowdown
        if self.collision_slowdown < 1.0:
            self.collision_slowdown = min(1.0, self.collision_slowdown + 0.01)
        
        # Steering: right hand Y position (appears as left due to mirror)
        if right_hand_y is not None:
            # Convert hand Y position to steering
            # Y position 0-1 (top to bottom) maps to left-right steering
            steering_input = (right_hand_y - 0.5) * 2  # -1 to 1
            self.steering_angle = steering_input * 0.1  # Scale steering sensitivity
            
            # Apply steering to car position
            self.car_x += self.steering_angle
            
            # Keep car within track bounds with some tolerance
            self.car_x = max(self.track_left + 0.15, min(self.track_right - 0.15, self.car_x))
        
        # Move car forward based on speed
        self.car_y += self.car_speed
        
        # Update lap time
        self.lap_time = time.time() - self.start_time
        
    def check_collisions(self):
        """Check for collisions with obstacles"""
        car_radius = 0.12
        
        for obstacle in self.obstacles:
            if obstacle['hit']:
                continue
                
            distance = math.sqrt((self.car_x - obstacle['x'])**2 + (self.car_y - obstacle['y'])**2)
            
            if distance < (car_radius + 0.12):  # Collision detected
                obstacle['hit'] = True
                # Apply temporary slowdown instead of stopping
                self.collision_slowdown = 0.3  # Reduce max speed to 30% for a while
                self.car_speed *= 0.4  # Immediate speed reduction
                # Add some visual feedback
                obstacle['hit_time'] = time.time()
                return True
        
        return False
    
    def update_obstacles(self):
        """Update obstacle positions and generate new ones"""
        # Move obstacles relative to car
        for obstacle in self.obstacles:
            obstacle['y'] -= self.car_speed
        
        # Remove obstacles that are behind the car
        self.obstacles = [obs for obs in self.obstacles if obs['y'] > self.car_y - 3]
        
        # Add new obstacles ahead
        while len(self.obstacles) < 8:
            max_y = max([obs['y'] for obs in self.obstacles]) if self.obstacles else self.car_y
            new_obstacle_x = random.uniform(self.track_left + 0.3, self.track_right - 0.3)
            new_obstacle_y = max_y + random.uniform(2.0, 4.0)
            self.obstacles.append({'x': new_obstacle_x, 'y': new_obstacle_y, 'hit': False})
        
        # Update score based on obstacles passed and distance traveled
        obstacles_passed = len([obs for obs in self.obstacles if obs['y'] < self.car_y - 1 and not obs['hit']])
        distance_bonus = int(self.car_y * 0.1)  # Bonus for distance traveled
        self.score = max(self.score, obstacles_passed + distance_bonus)
    
    def draw_track(self):
        """Draw the racing track"""
        # Get current view bounds
        view_bottom = self.car_y - 1
        view_top = self.car_y + 3
        
        # Track surface - extend beyond view bounds
        track_rect = patches.Rectangle(
            (self.track_left, view_bottom - 2), self.track_width, view_top - view_bottom + 4,
            facecolor=self.track_color, alpha=0.8
        )
        self.ax.add_patch(track_rect)
        
        # Track borders - extend beyond view bounds
        self.ax.plot([self.track_left, self.track_left], [view_bottom - 2, view_top + 2], 
                    color='white', linewidth=3)
        self.ax.plot([self.track_right, self.track_right], [view_bottom - 2, view_top + 2], 
                    color='white', linewidth=3)
        
        # Center line (dashed) - only draw in visible area
        for y in np.arange(view_bottom, view_top + 1, 0.5):
            self.ax.plot([self.track_center_x, self.track_center_x], [y, y + 0.2], 'yellow', linewidth=2)
    
    def draw_car(self):
        """Draw the race car"""
        # Car body
        car_rect = patches.Rectangle(
            (self.car_x - 0.1, self.car_y - 0.15), 0.2, 0.3,
            facecolor=self.car_color, edgecolor='darkred', linewidth=2
        )
        self.ax.add_patch(car_rect)
        
        # Car details (wheels)
        wheel_positions = [
            (self.car_x - 0.08, self.car_y - 0.1),
            (self.car_x + 0.08, self.car_y - 0.1),
            (self.car_x - 0.08, self.car_y + 0.1),
            (self.car_x + 0.08, self.car_y + 0.1)
        ]
        
        for wheel_x, wheel_y in wheel_positions:
            wheel = patches.Circle((wheel_x, wheel_y), 0.03, facecolor='black')
            self.ax.add_patch(wheel)
    
    def draw_obstacles(self):
        """Draw obstacles on the track"""
        for obstacle in self.obstacles:
            if abs(obstacle['y'] - self.car_y) < 4:  # Only draw nearby obstacles
                color = 'gray' if obstacle['hit'] else self.obstacle_color
                obstacle_rect = patches.Rectangle(
                    (obstacle['x'] - 0.1, obstacle['y'] - 0.1), 0.2, 0.2,
                    facecolor=color, edgecolor='black', linewidth=1
                )
                self.ax.add_patch(obstacle_rect)
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Get current view bounds for UI positioning
        view_bottom = self.car_y - 1
        view_top = self.car_y + 3
        
        # Speed indicator with collision effect (positioned relative to current view)
        speed_display = self.car_speed * 100
        speed_color = 'red' if self.collision_slowdown < 0.8 else 'white'
        speed_text = f"Speed: {speed_display:.0f} km/h"
        self.ax.text(0.2, view_top - 0.3, speed_text, fontsize=14, color=speed_color, weight='bold')
        
        # Score (positioned relative to current view)
        score_text = f"Score: {self.score}"
        self.ax.text(0.2, view_top - 0.6, score_text, fontsize=14, color='white', weight='bold')
        
        # Time (positioned relative to current view)
        time_text = f"Time: {self.lap_time:.1f}s"
        self.ax.text(0.2, view_top - 0.9, time_text, fontsize=14, color='white', weight='bold')
        
        # Collision status (positioned relative to current view)
        if self.collision_slowdown < 1.0:
            collision_text = f"⚠️ DAMAGED! Recovery: {self.collision_slowdown*100:.0f}%"
            self.ax.text(0.2, view_top - 1.2, collision_text, fontsize=12, color='orange', weight='bold')
        
        # Controls info (smaller and repositioned relative to current view)
        controls = [
            "🏎️ CONTROLS:",
            "Left Hand: Speed",
            "Right Hand: Steering",
            "Press 'R' to restart"
        ]
        
        for i, control in enumerate(controls):
            color = 'yellow' if i == 0 else 'lightblue'
            fontsize = 11 if i == 0 else 9
            weight = 'bold' if i == 0 else 'normal'
            self.ax.text(7.5, view_top - 0.3 - i * 0.25, control, fontsize=fontsize, 
                        color=color, weight=weight)
    
    def update_game(self, left_hand_distance, right_hand_distance, left_hand_y, right_hand_y):
        """Main game update function"""
        self.update_car_position(left_hand_distance, right_hand_distance, left_hand_y, right_hand_y)
        
        # Check if car went off track - just slow down instead of game over
        if self.car_x <= self.track_left or self.car_x >= self.track_right:
            self.car_speed *= 0.5  # Slow down when off track
            # Push car back onto track gently
            if self.car_x <= self.track_left:
                self.car_x = self.track_left + 0.1
            else:
                self.car_x = self.track_right - 0.1
        
        collision = self.check_collisions()
        self.update_obstacles()
    
    def draw_game(self):
        """Draw the complete game"""
        self.ax.clear()
        
        # Set view to follow car
        view_bottom = self.car_y - 1
        view_top = self.car_y + 3
        
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(view_bottom, view_top)  # Camera follows car
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('darkgreen')
        
        # Draw grass/background extending beyond track
        grass_left = patches.Rectangle(
            (0, view_bottom - 2), self.track_left, view_top - view_bottom + 4,
            facecolor='darkgreen', alpha=1.0
        )
        self.ax.add_patch(grass_left)
        
        grass_right = patches.Rectangle(
            (self.track_right, view_bottom - 2), 10 - self.track_right, view_top - view_bottom + 4,
            facecolor='darkgreen', alpha=1.0
        )
        self.ax.add_patch(grass_right)
        
        self.draw_track()
        self.draw_obstacles()
        self.draw_car()
        self.draw_ui()
        
        # Remove axes
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        plt.draw()
        plt.pause(0.01)
    
    def on_key_press(self, event):
        """Handle keyboard events in matplotlib window"""
        if event.key == 'r':
            self.key_pressed = 'r'
        elif event.key == 'q' or event.key == 'escape':
            self.key_pressed = 'q'
    
    def get_key_pressed(self):
        """Get and clear the last key pressed"""
        key = self.key_pressed
        self.key_pressed = None
        return key
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.car_x = 5.0
        self.car_y = 1.0
        self.car_speed = 0.0
        self.steering_angle = 0.0
        self.score = 0
        self.game_over = False
        self.collision_slowdown = 1.0
        self.start_time = time.time()
        self.generate_obstacles()
        print("🔄 Game restarted!")
    
    def close(self):
        """Close the game window"""
        plt.close(self.fig)


class HandGestureRecognizer:
    """Recognizes hand gestures for racing game control"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
    
    def calculate_distance(self, point1, point2) -> float:
        """Calculate distance between two landmarks"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def analyze_hand(self, hand_landmarks) -> dict:
        """Analyze hand for racing gestures"""
        landmarks = hand_landmarks.landmark
        
        # Get thumb tip and index finger tip for gap measurement
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Get wrist for hand position reference
        wrist = landmarks[0]
        
        # Calculate distance between thumb and index
        distance = self.calculate_distance(thumb_tip, index_tip)
        
        # Get average Y position of hand (for steering)
        hand_y = (thumb_tip.y + index_tip.y + wrist.y) / 3
        
        return {
            'thumb_index_distance': distance,
            'hand_y': hand_y,
            'landmarks': landmarks
        }
    
    def process_frame(self, frame) -> Tuple[dict, np.ndarray]:
        """Process frame and return gesture info"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture_info = {
            'left_hand': None,  # Note: This is actually right hand due to mirror
            'right_hand': None,  # Note: This is actually left hand due to mirror
            'hand_count': 0
        }
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_label = handedness.classification[0].label
                hand_analysis = self.analyze_hand(hand_landmarks)
                
                # Store based on detected label (camera is mirrored)
                if hand_label == 'Left':
                    gesture_info['left_hand'] = hand_analysis
                else:
                    gesture_info['right_hand'] = hand_analysis
                
                gesture_info['hand_count'] += 1
                
                # Draw landmarks with racing-themed colors
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=self.mp_draw.DrawingSpec(color=(255, 255, 0), thickness=2)
                )
        
        return gesture_info, frame


class RacingHandTracker:
    """Main racing game application"""
    
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.gesture_recognizer = HandGestureRecognizer()
        self.racing_game = RacingGame()
        
        # FPS calculation
        self.pTime = 0
        
        # Game control
        self.game_running = True
        
        # Set up camera window position and size
        self.camera_window_name = "🏁 Racing Camera Control"
        cv2.namedWindow(self.camera_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.camera_window_name, 400, 300)  # Smaller camera window
        cv2.moveWindow(self.camera_window_name, 50, 500)  # Position in bottom left
        
    def process_gestures(self, gesture_info):
        """Process gestures and update racing game"""
        # Extract hand data (remember camera is mirrored)
        left_hand_distance = None
        right_hand_distance = None
        left_hand_y = None
        right_hand_y = None
        
        # Left hand in camera = right hand in reality (speed control)
        if gesture_info['left_hand'] is not None:
            left_hand_distance = gesture_info['left_hand']['thumb_index_distance']
            left_hand_y = gesture_info['left_hand']['hand_y']
        
        # Right hand in camera = left hand in reality (steering)
        if gesture_info['right_hand'] is not None:
            right_hand_distance = gesture_info['right_hand']['thumb_index_distance']
            right_hand_y = gesture_info['right_hand']['hand_y']
        
        # Update racing game
        self.racing_game.update_game(left_hand_distance, right_hand_distance, left_hand_y, right_hand_y)
    
    def run(self):
        """Main game loop"""
        print("🏁 RACING HAND TRACKER STARTED! 🏁")
        print("=" * 60)
        print("🏎️  CONTROLS:")
        print("• LEFT HAND (Speed Control):")
        print("  - Small gap between thumb and index: BRAKE")
        print("  - Large gap between thumb and index: ACCELERATE")
        print("• RIGHT HAND (Steering):")
        print("  - Move hand UP: Turn LEFT")
        print("  - Move hand DOWN: Turn RIGHT")
        print("=" * 60)
        print("🎯 OBJECTIVE: Avoid orange obstacles and stay on track!")
        print("💡 TIP: Camera is mirrored - left/right hands are swapped")
        print("⌨️  KEYBOARD: Press 'q' to quit, 'r' to restart")
        print("🏆 NEW: Game never stops! Collisions just slow you down!")
        print("=" * 60)
        
        while self.game_running:
            success, frame = self.cap.read()
            if not success:
                continue
            
            # Process gestures
            gesture_info, annotated_frame = self.gesture_recognizer.process_frame(frame)
            self.process_gestures(gesture_info)
            
            # Calculate and display FPS
            cTime = time.time()
            fps = 1 / (cTime - self.pTime) if (cTime - self.pTime) > 0 else 0
            self.pTime = cTime
            
            # Add racing-themed UI to camera frame
            cv2.putText(annotated_frame, f"🏁 FPS: {int(fps)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"🏎️ Hands: {gesture_info['hand_count']}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show speed and steering info
            if gesture_info['left_hand']:  # Speed control hand
                distance = gesture_info['left_hand']['thumb_index_distance']
                if distance < 0.05:
                    action = "🛑 BRAKING"
                    color = (0, 0, 255)  # Red
                elif distance > 0.15:
                    action = "🚀 ACCELERATING"
                    color = (0, 255, 0)  # Green
                else:
                    action = "⚡ COASTING"
                    color = (0, 255, 255)  # Yellow
                
                cv2.putText(annotated_frame, action, 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            if gesture_info['right_hand']:  # Steering hand
                hand_y = gesture_info['right_hand']['hand_y']
                if hand_y < 0.4:
                    steering = "⬅️ LEFT"
                elif hand_y > 0.6:
                    steering = "➡️ RIGHT"
                else:
                    steering = "⬆️ STRAIGHT"
                
                cv2.putText(annotated_frame, steering, 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Game status
            if self.racing_game.collision_slowdown < 0.8:
                cv2.putText(annotated_frame, "⚠️ DAMAGED!", 
                           (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.putText(annotated_frame, f"Score: {self.racing_game.score}", 
                       (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(annotated_frame, f"Speed: {self.racing_game.car_speed*100:.0f} km/h", 
                       (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Display camera feed in positioned window
            cv2.imshow(self.camera_window_name, annotated_frame)
            
            # Update racing game visualization
            self.racing_game.draw_game()
            
            # Handle keyboard input - check both matplotlib and opencv windows
            key = cv2.waitKey(1) & 0xFF
            matplotlib_key = self.racing_game.get_key_pressed()
            
            if key == ord('q') or matplotlib_key == 'q':
                print("🛑 Quitting game...")
                break
            elif key == ord('r') or matplotlib_key == 'r':
                print("🔄 Restarting game...")
                self.racing_game.reset_game()
            
            # Check if matplotlib window still exists
            if not plt.get_fignums():
                print("🎮 Game window closed!")
                break
    
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        self.racing_game.close()


if __name__ == "__main__":
    game = RacingHandTracker()
    try:
        game.run()
    finally:
        game.cleanup()
