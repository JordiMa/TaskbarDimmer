# TaskbarDimmer

TaskbarDimmer is a script designed to reduce the brightness of the Windows taskbar to protect OLED screens. The script creates a semi-transparent black overlay above the taskbar, reducing brightness and preventing screen burn-in.

## Installation

1. Make sure Python is installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).

2. Install the necessary dependencies:
    ```sh
    pip install pyautogui pystray pillow
    ```

3. Download the `TaskbarDimmer.py` script and run it:
    ```sh
    python TaskbarDimmer.py
    ```

## Configuration

### Configurable Parameters

- **Taskbar Height**: Height of the taskbar in pixels.
- **Taskbar Detection Height**: Height for detecting the mouse to trigger the brightness effect.
- **Base Opacity (%)**: Opacity of the taskbar when the mouse is not hovering over it, in percentage (0 to 100).

### Configuration Interface

The configuration interface is accessible via the system tray icon. Right-click on the application icon in the system tray and select "Config" to open the configuration window.

1. Modify the parameters as needed.
2. Click "Save" to apply the changes.

The parameters are saved in a `config.json` file located in `Documents\JordiMA\TaskbarDimmer\config.json`.

## Usage

1. Launch the application by running the `TaskbarDimmer.py` script.
2. The application icon will appear in the system tray.
3. Use the system tray icon to access the configuration settings or to exit the application.

## Uninstallation

To uninstall TaskbarDimmer, simply delete the script files and the configuration directory located in `Documents\JordiMA\TaskbarDimmer`.

## Dependencies

- `pyautogui`
- `pystray`
- `Pillow`

## Compatibility

Currently, TaskbarDimmer is functional only on Windows. Versions for Linux and macOS are planned and will be released in the future.

## Contribution

Contributions are welcome! Please open an issue to discuss any changes you would like to make.

## License

TaskbarDimmer is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for more information.
