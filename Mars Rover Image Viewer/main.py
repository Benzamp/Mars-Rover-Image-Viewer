"""
Project: Mars Rover Image Viewer
Author: Ben Harrison
Date: April 11, 2024
Description: GUI for viewing and downloading NASA Mars Rover Images.
License: MIT License
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from PIL import ImageTk, Image
import requests
from io import BytesIO
import os
import tkinter.font as tkFont
import re
import webbrowser

class MarsRoverImageViewer:
    def __init__(self, master):
        self.master = master
        self.master.title('Mars Rover Image Viewer')
        self.version = "1.0"  # Define the version number

        # Set the background color
        self.dark_gray = '#1E1E1E'

        # Define custom style
        self.custom_style = ttk.Style()

        # Set background color for all widgets
        self.custom_style.configure('.', background=self.dark_gray)

        # Create widgets
        self.tabControl = ttk.Notebook(master)
        self.tabControl.pack(expand=1, fill="both")

        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text="Viewer")

        self.tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2, text="Settings")

        self.tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3, text="About")

        self.image_frame = tk.Frame(self.tab1, bg=self.dark_gray)
        self.image_frame.pack(side="top", fill="both", expand=True)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(pady=10)

        self.details_label = tk.Label(self.tab1, text='', wraplength=400, justify='left', bg=self.dark_gray, fg='white')
        self.details_label.pack(pady=5)

        self.button_frame_top = tk.Frame(self.tab1, bg=self.dark_gray)
        self.button_frame_top.pack(pady=10)

        self.download_button = tk.Button(self.button_frame_top, text='Download Image', command=self.download_image, width=20, bg='#333', fg='white')  # Set button colors
        self.download_button.pack(side='left', padx=(10, 5))

        self.fetch_recent_button = tk.Button(self.button_frame_top, text='Fetch Recent Images', command=self.fetch_recent_images, width=20, bg='#333', fg='white')  # Set button colors
        self.fetch_recent_button.pack(side='left', padx=(5, 10))

        self.button_frame_bottom = tk.Frame(self.tab1, bg=self.dark_gray)
        self.button_frame_bottom.pack(pady=10)

        self.prev_button = tk.Button(self.button_frame_bottom, text='◀ Previous', command=self.show_previous_image, width=10, bg='#333', fg='white')  # Set button colors
        self.prev_button.pack(side='left', padx=(10, 5))

        self.image_counter_label = tk.Label(self.button_frame_bottom, text='', bg=self.dark_gray, fg='white')
        self.image_counter_label.pack(side='left', padx=(5, 10))

        self.next_button = tk.Button(self.button_frame_bottom, text='Next ▶', command=self.show_next_image, width=10, bg='#333', fg='white')  # Set button colors
        self.next_button.pack(side='right', padx=(5, 10))

        self.date_frame = tk.Frame(self.tab1, bg=self.dark_gray)
        self.date_frame.pack(pady=5)

        self.retract_sol_button = tk.Button(self.date_frame, text='◀ -1 sol', command=self.decrease_sol, width=10, bg='#333', fg='white')
        self.retract_sol_button.pack(side='left', padx=(10, 5))

        self.advance_sol_button = tk.Button(self.date_frame, text='+1 sol ▶', command=self.increase_sol, width=10, bg='#333', fg='white')
        self.advance_sol_button.pack(side='right', padx=(5, 10))

        self.rover_frame = tk.Frame(self.tab1, bg=self.dark_gray)
        self.rover_frame.pack(pady=5)

        self.selected_rover = tk.StringVar(value='')  # None of the radio buttons selected by default
        self.rover_radios = []

        rovers = ['Curiosity', 'Opportunity', 'Spirit']
        for rover in rovers:
            radio = tk.Radiobutton(self.rover_frame, text=rover, variable=self.selected_rover, value=rover, bg=self.dark_gray, fg='white', selectcolor=self.dark_gray)  # Set radio button colors
            radio.pack(side='left', padx=10)
            self.rover_radios.append(radio)

        self.date_frame = tk.Frame(self.tab1, bg=self.dark_gray)
        self.date_frame.pack(pady=5)

        self.date_label = tk.Label(self.date_frame, text='Select Martian Date (sol):', bg=self.dark_gray, fg='white')  # Set label colors
        self.date_label.pack(side='left')

        self.selected_date = tk.StringVar()
        self.date_entry = tk.Entry(self.date_frame, textvariable=self.selected_date, bg='#333', fg='white')  # Set entry colors
        self.date_entry.pack(side='left')

        self.fetch_button = tk.Button(self.date_frame, text='Search', command=self.fetch_and_display_images, width=7, bg='#333', fg='white')  # Set button colors
        self.fetch_button.pack(side='left', padx=(5, 10))

        self.console = scrolledtext.ScrolledText(self.tab1, wrap=tk.WORD, width=60, height=10, bg='#333', fg='white')  # Set console colors
        self.console.pack(pady=10, padx=10, fill='both', expand=True)

        self.settings_frame = tk.Frame(self.tab2, bg=self.dark_gray)
        self.settings_frame.pack(pady=10)

        # Frame for the first line of widgets
        self.api_key_frame = tk.Frame(self.settings_frame, bg=self.dark_gray)
        self.api_key_frame.pack(pady=5)

        # API key label
        self.api_key_label = tk.Label(self.api_key_frame, text='Enter API Key:', bg=self.dark_gray, fg='white')
        self.api_key_label.pack(side='left')

        # API key entry
        self.api_key_entry = tk.Entry(self.api_key_frame, bg='#333', fg='white')
        self.api_key_entry.pack(side='left')
        self.api_key = self.load_api_key()  # Load API key from file
        self.api_key_entry.insert(0, self.api_key)  # Auto-populate API key entry

        # Save API key button
        self.save_api_key_button = tk.Button(self.api_key_frame, text='Save API Key', command=self.save_api_key, bg='#333', fg='white')
        self.save_api_key_button.pack(side='left', padx=10)

        # Frame for the second line of widgets
        self.path_frame = tk.Frame(self.settings_frame, bg=self.dark_gray)
        self.path_frame.pack(pady=5)

        # Label for the download path entry
        self.download_path_label = tk.Label(self.path_frame, text="Download Path:", bg=self.dark_gray, fg='white')
        self.download_path_label.pack(side='left')

        # Create a download path entry widget
        self.download_path_entry = tk.Entry(self.path_frame, bg='#333', fg='white')
        self.download_path_entry.pack(side='left', expand=True, fill='x')

        # Load download path from file
        self.download_path = self.load_download_path()
        self.download_path_entry.insert(0, self.download_path)

        # Browse button for selecting download path
        self.browse_button = tk.Button(self.path_frame, text="Browse", command=self.browse_download_path, bg='#333', fg='white')
        self.browse_button.pack(side='left', padx=(5, 10))

        self.save_path_button = tk.Button(self.path_frame, text="Save", command=self.save_download_path, bg='#333', fg='white')
        self.save_path_button.pack(side='left', padx=(5, 10))

        self.about_text = scrolledtext.ScrolledText(self.tab3, wrap=tk.WORD, width=60, height=10, bg='#333', fg='white')  # Set text widget colors
        self.about_text.pack(pady=10, padx=10, fill='both', expand=True)
        self.load_readme()

        self.about_label = tk.Label(self.tab3, text=f"Made by Ben Harrison\nGithub: https://github.com/Benzamp\nVersion: {self.version}", bg=self.dark_gray, fg='white')  # Set label colors
        self.about_label.pack(side='bottom', pady=(0, 10), padx=10, anchor='center')

        self.current_index = 0
        self.photos = []
        self.image_displayed = False  # Track if an image is currently being displayed

        # Get the full path of the font file
        font_file = os.path.join(os.path.dirname(__file__), 'fonts/VcrOsd.ttf')

        # Register the custom font with Tkinter
        self.custom_font = tkFont.Font(font=tkFont.Font(family='VCR OSD Mono', size=11))

        # Apply the custom font to widgets
        self.image_label.config(font=self.custom_font)
        self.details_label.config(font=self.custom_font)
        self.console.config(font=self.custom_font)
        self.api_key_label.config(font=self.custom_font)
        self.api_key_entry.config(font=self.custom_font)
        self.save_api_key_button.config(font=self.custom_font)
        self.about_text.config(font=self.custom_font)

        # Apply custom font to all radio buttons
        for radio in self.rover_radios:
            radio.config(font=self.custom_font)

        self.date_entry.config(font=self.custom_font)
        self.date_label.config(font=self.custom_font)
        self.fetch_button.config(font=self.custom_font)
        self.download_button.config(font=self.custom_font)
        self.prev_button.config(font=self.custom_font)
        self.next_button.config(font=self.custom_font)
        self.image_counter_label.config(font=self.custom_font)
        self.download_path_label.config(font=self.custom_font)
        self.browse_button.config(font=self.custom_font)
        self.fetch_recent_button.config(font=self.custom_font)
        self.retract_sol_button.config(font=self.custom_font)
        self.advance_sol_button.config(font=self.custom_font)
        self.save_path_button.config(font=self.custom_font)

        # Set the background color of button frames
        self.button_frame_top.config(bg=self.dark_gray)
        self.button_frame_bottom.config(bg=self.dark_gray)

        # Set minimum height and width of the window
        self.master.minsize(625, 850)
        self.master.maxsize(625, 850)

        # Set a placeholder image when the app is started
        self.display_current_image_placeholder()

        self.sol = None

        # Check if API key is set and verified
        if self.check_api_key():
            initial_message = "Choose a rover and search for images by entering a specific sol date, or simply fetch the most recent images and explore from there."
        else:
            initial_message = "You need to add an API key. If you need one, go to the About tab for instructions. If you have one, add it in the Settings tab."

        self.display_message(initial_message)

    def fetch_recent_images(self):
        rover_name = self.selected_rover.get()
        sol = 'latest_photos'
        rovers = [rover_name.lower()]
        
        # Display message in console
        self.display_message(f"Getting most recent images from {rover_name}...")  

        self.photos = []

        for rover in rovers:
            url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/latest_photos?api_key={self.api_key}'

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    self.photos.extend(data['latest_photos'])
                    # Extract the sol date from the fetched data
                    if data['latest_photos']:
                        sol_date = data['latest_photos'][0]['sol']
                        # Update the selected date field
                        self.selected_date.set(str(sol_date))
                else:
                    self.display_message(f'Failed to fetch recent photos for {rover}: {response.status_code}')
            except Exception as e:
                self.display_message('An error occurred:', str(e))

        if self.photos:
            self.current_index = 0
            self.display_current_image()
        else:
            self.display_message('No recent photos available for the selected rover')

    def display_current_image(self):
        # Show a placeholder image initially
        placeholder_image = Image.new("RGB", (400, 400), color=self.dark_gray)
        placeholder_image = ImageTk.PhotoImage(placeholder_image)
        self.image_label.config(image=placeholder_image)
        self.image_label.image = placeholder_image

        # Fetch and display the actual image
        photo = self.photos[self.current_index]
        img_url = photo['img_src']
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            img_data = img_response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((400, 400))
            img = ImageTk.PhotoImage(img)
            self.image_label.config(image=img)
            self.image_label.image = img

            rover_name = photo['rover']['name']
            earth_date = photo['earth_date']
            sol = photo['sol']  # Martian date (sol)
            status = photo['rover']['status']
            self.details_label.config(text=f'Rover: {rover_name}\nEarth Date: {earth_date}\nMartian Date (sol): {sol}\nStatus: {status}')
            self.current_image_data = img_data  # Save image data for download

            # Update image counter
            self.image_counter_label.config(text=f'{self.current_index + 1}/{len(self.photos)}')
        else:
            self.display_message('Failed to fetch image:', img_response.status_code)


    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()

    def show_next_image(self):
        if self.current_index < len(self.photos) - 1:
            self.current_index += 1
            self.display_current_image()

    def download_image(self):
        if hasattr(self, 'current_image_data'):
            # Check if download path is set
            download_path = self.download_path_entry.get()
            if not download_path:
                self.display_message("Configure download path in the Settings tab.")
                return

            rover_name = self.photos[self.current_index]['rover']['name']
            earth_date = self.photos[self.current_index]['earth_date']
            image_number = self.current_index + 1  # Image number
            file_name = f"{rover_name}_{earth_date}_Image{image_number}.jpg"

            file_path = os.path.join(download_path, file_name)

            with open(file_path, 'wb') as f:
                f.write(self.current_image_data)
            self.display_message("Image downloaded successfully.")
        else:
            self.display_message("No image to download.")



    def save_api_key(self):
        self.api_key = self.api_key_entry.get()
        if self.check_api_key():
            messagebox.showinfo("Success", "API Key saved successfully and validated.")
            self.save_api_key_to_file()  # Save API key to file
        else:
            messagebox.showerror("Error", "Invalid API Key.")

    def check_api_key(self):
        url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={self.api_key}'
        try:
            response = requests.get(url)
            return response.status_code == 200
        except:
            return False

    def display_message(self, message):
        # Clear the console
        self.console.delete('1.0', tk.END)

        # Insert the new message
        self.console.insert(tk.END, f'{message}\n')
        self.console.see(tk.END)


    def load_api_key(self):
        try:
            with open('api_key.txt', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if not line.startswith('//') and line != '':
                        # Return the API key extracted from the file
                        return line
            # If no valid API key found
            print("No valid API key found")
            return ''
        except FileNotFoundError:
            print("File not found")  # Add this line to indicate file not found
            return ''
        
    def load_download_path(self):
        try:
            with open('api_key.txt', 'r') as f:
                lines = f.readlines()
                # Iterate through the lines to find the second uncommented line
                uncommented_count = 0
                for line in lines:
                    line = line.strip()
                    if not line.startswith('//') and line != '':
                        uncommented_count += 1
                        if uncommented_count == 2:  # Second uncommented line
                            # Extract the download path from the line
                            return line
            # If no valid download path found
            print("No valid download path found")
            return ''
        except FileNotFoundError:
            print("File not found")  # Add this line to indicate file not found
            return ''


    def save_api_key_to_file(self):
        api_key = self.api_key_entry.get()
        try:
            with open('api_key.txt', 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        if len(lines) >= 3:
            lines[2] = f'{api_key}\n'  # Save the API key directly without any prefix
        else:
            lines.append('\n' * (2 - len(lines)))  # Make sure there are at least 3 lines
            lines.append(f'{api_key}\n')

        with open('api_key.txt', 'w') as f:
            f.writelines(lines)


    def load_readme(self):
        try:
            with open('about.md', 'r') as f:
                readme_content = f.read()
                self.about_text.insert(tk.END, readme_content)
                self.about_text.configure(state='disabled')  # Disable editing of the text widget

                # Apply a tag to URLs in the text widget
                #self.apply_link_style() cant really get this to work right yet, gonna move on

        except FileNotFoundError:
            self.about_text.insert(tk.END, 'about.md not found.')

    def apply_link_style(self):
        # Regular expression to match URLs
        url_pattern = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])'

        # Find all URLs in the text widget content
        for match in re.finditer(url_pattern, self.about_text.get('1.0', 'end')):
            start_idx, end_idx = match.span()
            self.about_text.tag_add('url', f'1.0+{start_idx}c', f'1.0+{end_idx}c')

        # Configure tag to make URLs clickable
        self.about_text.tag_configure('url', foreground='blue', underline=True)

        # Bind callback function to handle click event on URLs
        #self.about_text.tag_bind('url', '<Button-1>', self.open_url)

    def display_current_image_placeholder(self):
        # Create a placeholder image
        placeholder_image = Image.new("RGB", (400, 400), color=self.dark_gray)
        placeholder_image = ImageTk.PhotoImage(placeholder_image)
        self.image_label.config(image=placeholder_image)
        self.image_label.image = placeholder_image

    def fetch_and_display_images(self):
        rover_name = self.selected_rover.get()
        sol = self.selected_date.get()
        if not sol.isdigit():
            self.display_message('Please enter a valid sol number.')
            return

        rovers = [rover_name.lower()]

        self.photos = []

        for rover in rovers:
            url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?sol={sol}&api_key={self.api_key}'

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    fetched_photos = data.get('photos', [])
                    if fetched_photos:
                        self.photos.extend(fetched_photos)
                        self.display_message(f"{len(fetched_photos)} images were found for the rover {rover_name} in sol year {sol}")
                    else:
                        self.display_message(f'No photos found for {rover_name} in sol year {sol}')
                        # Update image counter label when no photos are available
                        self.image_counter_label.config(text='0/0')
                        # Revert to placeholder image and nullify image facts
                        self.display_current_image_placeholder()
                        self.details_label.config(text='')
                        return  # Exit the method since there are no photos
                else:
                    self.display_message(f'Failed to fetch photos for {rover}: {response.status_code}')
                    # Update image counter label when fetching photos fails
                    self.image_counter_label.config(text='0/0')
                    # Revert to placeholder image and nullify image facts
                    self.display_current_image_placeholder()
                    self.details_label.config(text='')
                    return  # Exit the method since there are no photos
            except Exception as e:
                self.display_message('An error occurred:', str(e))
                # Update image counter label when an error occurs
                self.image_counter_label.config(text='0/0')
                # Revert to placeholder image and nullify image facts
                self.display_current_image_placeholder()
                self.details_label.config(text='')
                return  # Exit the method since there are no photos

        if self.photos:
            self.current_index = 0
            self.display_current_image()




    def fetch_recent_images(self):
        rover_name = self.selected_rover.get()
        rovers = [rover_name.lower()]
        
        self.display_message(f"Getting most recent images from {rover_name}...")  

        self.photos = []

        for rover in rovers:
            url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/latest_photos?api_key={self.api_key}'

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    latest_photos = data.get('latest_photos', [])
                    if latest_photos:
                        self.photos.extend(latest_photos)
                        sol_date = latest_photos[0]['sol']
                        self.selected_date.set(str(sol_date))
                        self.sol = str(sol_date)  
                        self.display_message(f"{len(latest_photos)} images were found for the rover {rover_name} in sol year {sol_date}")
                    else:
                        self.display_message(f'No recent photos available for {rover}')
                else:
                    self.display_message(f'Failed to fetch recent photos for {rover}: {response.status_code}')
            except Exception as e:
                self.display_message('An error occurred:', str(e))

        if self.photos:
            self.current_index = 0
            self.display_current_image()
        else:
            self.display_message('No recent photos available for the selected rover')

    def decrease_sol(self):
        current_sol = self.selected_date.get()
        if current_sol.isdigit() and int(current_sol) > 0:
            new_sol = int(current_sol) - 1
            self.selected_date.set(str(new_sol))
            self.sol = str(new_sol)  
            self.display_message(f"Fetching images for sol year {new_sol}...")  # Display message in console
            self.fetch_and_display_images()

    def increase_sol(self):
        current_sol = self.selected_date.get()
        if current_sol.isdigit():
            new_sol = int(current_sol) + 1
            self.selected_date.set(str(new_sol))
            self.sol = str(new_sol)  
            self.display_message(f"Fetching images for sol year {new_sol}...")  # Display message in console
            self.fetch_and_display_images()

    def fetch_rover_names(self):
            url = "https://api.nasa.gov/mars-photos/api/v1/rovers/?api_key=DEMO_KEY"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    self.rovers = [rover['name'].lower() for rover in data['rovers']]
                else:
                    self.rovers = ['curiosity', 'opportunity', 'spirit']  # Default rover names
            except Exception as e:
                print("An error occurred while fetching rover names:", str(e))
                self.rovers = ['curiosity', 'opportunity', 'spirit']  # Default rover names

    def browse_download_path(self):
        download_path = filedialog.askdirectory()
        if download_path:
            self.download_path_entry.delete(0, tk.END)
            self.download_path_entry.insert(0, download_path)

    def download_image(self):
        if hasattr(self, 'current_image_data'):
            rover_name = self.photos[self.current_index]['rover']['name']
            earth_date = self.photos[self.current_index]['earth_date']
            image_number = self.current_index + 1  # Image number
            file_name = f"{rover_name}_{earth_date}_Image{image_number}.jpg"

            download_path = self.download_path_entry.get()
            if not download_path:
                file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                        filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
                                                        initialfile=file_name)
            else:
                file_path = os.path.join(download_path, file_name)

            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(self.current_image_data)
                self.display_message("Image downloaded successfully.")
        else:
            self.display_message("No image to download.")

    def save_download_path(self):
        download_path = self.download_path_entry.get()
        if download_path:
            try:
                # Open the api_key.txt file and read its contents
                with open('api_key.txt', 'r') as f:
                    lines = f.readlines()
                
                # Update the download path in the fourth line
                if len(lines) >= 4:
                    lines[3] = f'{download_path}\n'
                else:
                    lines.append('\n' * (3 - len(lines)))
                    lines.append(f'{download_path}\n')

                # Write the updated contents back to the file
                with open('api_key.txt', 'w') as f:
                    f.writelines(lines)

                messagebox.showinfo("Success", "Download path saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showerror("Error", "Download path cannot be empty.")

def main():
    window = tk.Tk()
    window.iconphoto(True, tk.PhotoImage(file='Images/rover-icon2.png'))
    app = MarsRoverImageViewer(window)
    window.mainloop()

if __name__ == "__main__":
    main()
