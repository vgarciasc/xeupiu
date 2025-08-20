import sys

if sys.platform == "win32":
    from xeupiu.windows.screenshot import get_window_by_title, get_window_image, get_window_base_dims
elif sys.platform == "linux":
    from xeupiu.linux.screenshot import get_window_by_title, get_window_image, get_window_base_dims
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

if __name__ == "__main__":
    # Capture the entire screen
    # screen_pixels = capture_pixels("VLC")
    # if screen_pixels:
    #     screen_pixels.save("data/tmp.png")

    # Capture a specific window
    window_id = get_window_by_title("Tokimeki Memorial")
    get_window_base_dims(window_id)
    window_pixels = get_window_image(window_id)
    if window_pixels:
        window_pixels.save("data/test/ss.png")
    

    # tik = time.perf_counter()
    # for _ in range(100):
    #     window_id = get_window_by_title("Tokimeki Memorial")
    #     window_pixels = get_window_image(window_id)
    # tok = time.perf_counter()
    # print(f"Capturing the window took {(tok - tik)/100*1000} miliseconds on average.")
