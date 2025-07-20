import tkinter as tk
from PIL import Image, ImageDraw
import numpy as np
import time
import threading

class DigitCaptureApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Digit Capture")
        
        # Make fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=self.screen_width, 
            height=self.screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Drawing variables
        self.old_x = None
        self.old_y = None
        self.line_width = 15
        
        # Create PIL image for capturing the drawing
        self.image = Image.new('L', (self.screen_width, self.screen_height), 'black')
        self.draw = ImageDraw.Draw(self.image)
        
        # Bind mouse/touch events
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw_line)
        self.canvas.bind('<ButtonRelease-1>', self.stop_draw)
        
        # Bind escape key to exit
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Add instruction text
        self.instruction_text = self.canvas.create_text(
            self.screen_width // 2,
            50,
            text="Draw a digit (0-9) - Canvas resets every 30 seconds - Press ESC to exit",
            fill='white',
            font=('Arial', 20)
        )
        
        # Timer display
        self.timer_text = self.canvas.create_text(
            self.screen_width - 100,
            50,
            text="Time: 30s",
            fill='white',
            font=('Arial', 16)
        )
        
        # Start the reset timer
        self.start_time = time.time()
        self.update_timer()
        
    def start_draw(self, event):
        """Start drawing when mouse/stylus is pressed"""
        self.old_x = event.x
        self.old_y = event.y
        
    def draw_line(self, event):
        """Draw line as mouse/stylus moves"""
        if self.old_x and self.old_y:
            # Draw on canvas
            self.canvas.create_line(
                self.old_x, self.old_y, event.x, event.y,
                width=self.line_width, fill='white',
                capstyle=tk.ROUND, smooth=tk.TRUE
            )
            
            # Draw on PIL image
            self.draw.line(
                [self.old_x, self.old_y, event.x, event.y],
                fill='white', width=self.line_width
            )
            
            self.old_x = event.x
            self.old_y = event.y
    
    def stop_draw(self, event):
        """Stop drawing when mouse/stylus is released"""
        self.old_x = None
        self.old_y = None
    
    def process_drawing(self):
        """Process the drawn image to 28x28 MNIST format"""
        # Find bounding box of the drawing
        bbox = self.image.getbbox()
        
        if bbox:
            # Crop to the bounding box
            cropped = self.image.crop(bbox)
            
            # Calculate padding to make it square
            width, height = cropped.size
            max_dim = max(width, height)
            
            # Create square image with padding
            square_img = Image.new('L', (max_dim, max_dim), 'black')
            offset_x = (max_dim - width) // 2
            offset_y = (max_dim - height) // 2
            square_img.paste(cropped, (offset_x, offset_y))
            
            # Add extra padding (20% on each side)
            padding = int(max_dim * 0.2)
            padded_size = max_dim + 2 * padding
            padded_img = Image.new('L', (padded_size, padded_size), 'black')
            padded_img.paste(square_img, (padding, padding))
            
            # Resize to 28x28
            # Use Image.LANCZOS for compatibility with older Pillow versions
            try:
                # Try newer syntax first (Pillow >= 9.1.0)
                mnist_img = padded_img.resize((28, 28), Image.Resampling.LANCZOS)
            except AttributeError:
                # Fall back to older syntax for Pillow < 9.1.0
                mnist_img = padded_img.resize((28, 28), Image.LANCZOS)
            
            # Convert to numpy array and normalize to 0-1
            mnist_array = np.array(mnist_img, dtype=np.float32) / 255.0
            
            # Print the result
            print("\n" + "="*50)
            print("Captured digit as 28x28 matrix (normalized 0-1):")
            print("="*50)
            
            # Print with formatting
            for row in mnist_array:
                print(' '.join([f'{val:.2f}' for val in row]))
            
            # Also print a visual representation
            print("\nVisual representation:")
            for row in mnist_array:
                print(''.join(['█' if val > 0.5 else '▒' if val > 0.1 else ' ' for val in row]))
            
            return mnist_array
        else:
            print("\nNo drawing detected!")
            return None
    
    def reset_canvas(self):
        """Clear the canvas and reset for new input"""
        # Process current drawing before clearing
        self.process_drawing()
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Recreate instruction text
        self.instruction_text = self.canvas.create_text(
            self.screen_width // 2,
            50,
            text="Draw a digit (0-9) - Canvas resets every 30 seconds - Press ESC to exit",
            fill='white',
            font=('Arial', 20)
        )
        
        # Recreate timer text
        self.timer_text = self.canvas.create_text(
            self.screen_width - 100,
            50,
            text="Time: 30s",
            fill='white',
            font=('Arial', 16)
        )
        
        # Clear PIL image
        self.image = Image.new('L', (self.screen_width, self.screen_height), 'black')
        self.draw = ImageDraw.Draw(self.image)
        
        # Reset timer
        self.start_time = time.time()
        print("\n" + "="*50)
        print("Canvas reset - Ready for new input")
        print("="*50)
    
    def update_timer(self):
        """Update the timer display and reset after 30 seconds"""
        elapsed = time.time() - self.start_time
        remaining = max(0, 30 - int(elapsed))
        
        # Update timer text
        self.canvas.itemconfig(self.timer_text, text=f"Time: {remaining}s")
        
        if elapsed >= 30:
            self.reset_canvas()
        
        # Schedule next update
        self.root.after(100, self.update_timer)
    
    def run(self):
        """Start the application"""
        print("Digit Capture Application Started")
        print("- Draw digits with mouse/stylus")
        print("- Canvas automatically resets every 30 seconds")
        print("- Press ESC to exit")
        print("="*50)
        
        self.root.mainloop()


if __name__ == "__main__":
    app = DigitCaptureApp()
    app.run()
