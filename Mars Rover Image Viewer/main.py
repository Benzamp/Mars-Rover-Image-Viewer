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
from datetime import datetime
import threading
import json

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

        # Create a button to fetch the saved image
        #self.fetch_saved_image_button = tk.Button(self.tab1, text='Load Saved Image', command=self.load_saved_image_info, width=40, bg='#333', fg='white')
        #self.fetch_saved_image_button.pack(pady=10)

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
        self.save_api_key_button = tk.Button(self.api_key_frame, text='Save API Key', command=self.save_api_key_to_file, bg='#333', fg='white')
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
        #self.fetch_saved_image_button.config(font=self.custom_font)
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

    def display_image(self, img_data):
        # Display the image
        with Image.open(BytesIO(img_data)) as img:
            img = img.resize((400, 400))
            img = ImageTk.PhotoImage(img)
            self.image_label.config(image=img)
            self.image_label.image = img

    def fetch_image(self, img_url):
        try:
            # Fetch the image data
            img_response = requests.get(img_url)
            img_response.raise_for_status()  # Raise an exception for non-200 responses
            img_data = img_response.content
            self.display_image(img_data)
        except requests.exceptions.RequestException as e:
            self.display_message(f'Failed to fetch image: {e}')

    def display_current_image(self):
        # Show a placeholder image initially
        placeholder_image = Image.new("RGB", (400, 400), color=self.dark_gray)
        placeholder_image = ImageTk.PhotoImage(placeholder_image)
        self.image_label.config(image=placeholder_image)
        self.image_label.image = placeholder_image

        # Fetch and display the actual image asynchronously
        photo = self.photos[self.current_index]
        img_url = photo['img_src']
        threading.Thread(target=self.fetch_image, args=(img_url,)).start()

        rover_name = photo['rover']['name']
        earth_date = photo['earth_date']
        sol = photo['sol']  # Martian date (sol)
        status = photo['rover']['status']
        self.details_label.config(text=f'Rover: {rover_name}\nEarth Date: {earth_date}\nMartian Date (sol): {sol}\nStatus: {status}')

        # Update image counter
        self.image_counter_label.config(text=f'{self.current_index + 1}/{len(self.photos)}')

    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()

    def show_next_image(self):
        if self.current_index < len(self.photos) - 1:
            self.current_index += 1
            self.display_current_image()

    def download_image(self):
        # Check if download path is set
        download_path = self.download_path_entry.get()
        if not download_path:
            self.display_message("Configure download path in the Settings tab.")
            return

        rover_name = self.photos[self.current_index]['rover']['name']
        earth_date = self.photos[self.current_index]['earth_date']
        image_number = self.current_index + 1  # Image number
        file_name = f"{rover_name}_{earth_date}_Image{image_number}.jpg"
        img_url = self.photos[self.current_index]['img_src']

        file_path = os.path.join(download_path, file_name)

        try:
            response = requests.get(img_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                self.display_message("Image downloaded successfully.")
            else:
                self.display_message(f"Failed to download image. Status code: {response.status_code}")
        except Exception as e:
            self.display_message(f"Error downloading image: {e}")

        def check_api_key(self):
            url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={self.api_key}'
            try:
                response = requests.get(url)
                return response.status_code == 200
            except:
                return False

    def display_message(self, message):
        # Insert the new message
        self.console.insert(tk.END, f'{message}\n')
        self.console.see(tk.END)

    def load_api_key(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                return settings.get("apiKey", "")
        except FileNotFoundError:
            print("File not found")
            return ''
        
    def load_download_path(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                return settings.get("downloadPath", "")
        except FileNotFoundError:
            print("File not found")
            return ''

    def save_api_key_to_file(self):
        api_key = self.api_key_entry.get()
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}

        settings["apiKey"] = api_key

        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

    def save_image_info_to_file(self, rover_name, sol_date, image_number):
        info = {
            "rover_name": rover_name,
            "sol_date": sol_date,
            "image_number": image_number,
            "saved_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}

        settings["saveLocation"] = info

        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

    def load_saved_image_info(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                save_location = settings.get("saveLocation")
                if save_location:
                    rover_name = save_location.get("rover_name")
                    sol_date = save_location.get("sol_date")
                    image_number = save_location.get("image_number")
                    saved_datetime = save_location.get("saved_datetime")

                    # Display the message in the Viewer's scrollable text
                    message = f"From {saved_datetime}: {rover_name} Sol:{sol_date} #{image_number}"
                    self.display_message(message)
                else:
                    self.display_message("No saved image info found.")
        except FileNotFoundError:
            self.display_message("File not found")
        except Exception as e:
            self.display_message("An error occurred while loading saved image info: " + str(e))


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

    def saved_image_data_exists(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                save_location = settings.get("saveLocation")
                if save_location:
                    return True
                else:
                    return False
        except FileNotFoundError:
            return False

    def display_current_image_placeholder(self):
        # Create a placeholder image
        placeholder_image = Image.new("RGB", (400, 400), color=self.dark_gray)
        placeholder_image = ImageTk.PhotoImage(placeholder_image)
        self.image_label.config(image=placeholder_image)
        self.image_label.image = placeholder_image

        # Check if there is saved information in saveLocation
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                save_location = settings.get("saveLocation")
                if save_location:
                    # Format the message with the saved information
                    rover_name = save_location.get("rover_name")
                    sol_date = save_location.get("sol_date")
                    image_number = save_location.get("image_number")
                    saved_datetime = save_location.get("saved_datetime")
                    message = f"Saved image info:\nRover: {rover_name}\nSol Date: {sol_date}\nImage Number: {image_number}\nSaved DateTime: {saved_datetime}"
                    self.display_message(message)
                else:
                    initial_message = "Choose a rover and search for images by entering a specific sol date, or simply fetch the most recent images and explore from there."
                    self.display_message(initial_message)
        except FileNotFoundError:
            initial_message = "Choose a rover and search for images by entering a specific sol date, or simply fetch the most recent images and explore from there."
            self.display_message(initial_message)
        except Exception as e:
            initial_message = "An error occurred while loading saved image info: " + str(e)
            self.display_message(initial_message)

    def fetch_and_display_images(self):
        # Clear the console
        self.console.delete('1.0', tk.END)

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
                        # Clear the console
                        self.console.delete('1.0', tk.END)
                        # Update image counter label when no photos are available
                        self.image_counter_label.config(text='0/0')
                        # Revert to placeholder image and nullify image facts
                        self.display_current_image_placeholder()
                        # Set the message in the Viewer's scrollable text
                        self.display_message(f'No images found for {rover_name} on sol {sol}')
                        return  # Exit the method since there are no photos
                else:
                    # Clear the console
                    self.console.delete('1.0', tk.END)

                    # Update image counter label when fetching photos fails
                    self.image_counter_label.config(text='0/0')
                    # Revert to placeholder image and nullify image facts
                    self.display_current_image_placeholder()
                    # Set the message in the Viewer's scrollable text
                    self.display_message(f'Failed to fetch images for {rover_name} on sol {sol}')
                    return  # Exit the method since there are no photos
            except Exception as e:
                # Clear the console
                self.console.delete('1.0', tk.END)
                # Update image counter label when an error occurs
                self.image_counter_label.config(text='0/0')
                # Revert to placeholder image and nullify image facts
                self.display_current_image_placeholder()
                # Set the message in the Viewer's scrollable text
                self.display_message(f'Error fetching images for {rover_name} on sol {sol}')
                return  # Exit the method since there are no photos

        if self.photos:
            self.current_index = 0
            self.display_current_image()

    def fetch_and_display_images(self):
        # Clear the console
        self.console.delete('1.0', tk.END)

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
                        # Clear the console
                        self.console.delete('1.0', tk.END)
                        # Update image counter label when no photos are available
                        self.image_counter_label.config(text='0/0')
                        # Revert to placeholder image and nullify image facts
                        self.display_current_image_placeholder()
                        # Set the message in the Viewer's scrollable text
                        self.display_message(f'No images found for {rover_name} on sol {sol}')
                        return  # Exit the method since there are no photos
                else:
                    # Clear the console
                    self.console.delete('1.0', tk.END)

                    # Update image counter label when fetching photos fails
                    self.image_counter_label.config(text='0/0')
                    # Revert to placeholder image and nullify image facts
                    self.display_current_image_placeholder()
                    # Set the message in the Viewer's scrollable text
                    self.display_message(f'Failed to fetch images for {rover_name} on sol {sol}')
                    return  # Exit the method since there are no photos
            except Exception as e:
                # Clear the console
                self.console.delete('1.0', tk.END)
                # Update image counter label when an error occurs
                self.image_counter_label.config(text='0/0')
                # Revert to placeholder image and nullify image facts
                self.display_current_image_placeholder()
                # Set the message in the Viewer's scrollable text
                self.display_message(f'Error fetching images for {rover_name} on sol {sol}')
                return  # Exit the method since there are no photos

        if self.photos:
            self.current_index = 0
            self.display_current_image()


    def fetch_recent_images(self):
        # Clear the console
        self.console.delete('1.0', tk.END)

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
            # Clear the console
            self.console.delete('1.0', tk.END)

            self.display_message(f"Fetching images for sol year {new_sol}...")  # Display message in console
            self.fetch_and_display_images()

    def increase_sol(self):
        current_sol = self.selected_date.get()
        if current_sol.isdigit():
            new_sol = int(current_sol) + 1
            self.selected_date.set(str(new_sol))
            self.sol = str(new_sol)

            # Clear the console
            self.console.delete('1.0', tk.END)

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

    

    def save_download_path(self):
        download_path = self.download_path_entry.get()
        if download_path:
            try:
                # Open the settings.json file and load its contents
                with open('settings.json', 'r') as f:
                    settings = json.load(f)

                # Update the download path in the settings
                settings['downloadPath'] = download_path

                # Write the updated contents back to the file
                with open('settings.json', 'w') as f:
                    json.dump(settings, f, indent=4)

                messagebox.showinfo("Success", "Download path saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showerror("Error", "Download path cannot be empty.")

def main():
    window = tk.Tk()
    window.iconphoto(True, tk.PhotoImage(file='Images/rover-icon2.png'))
    app = MarsRoverImageViewer(window)

    def on_closing():
        if messagebox.askokcancel("Quit", "Would you like to save your place so you can browse later?"):
            # Run the save_image_info_to_file function
            app.save_image_info_to_file(app.selected_rover.get(), app.selected_date.get(), app.current_index + 1)
            messagebox.showinfo("Success", "Your place has been saved successfully.")
        window.destroy()
    
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()


if __name__ == "__main__":
    main()
