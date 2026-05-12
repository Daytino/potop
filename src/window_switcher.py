class WindowSwitcher:
    def __init__(self):
        self.windows = dict()
        self.current_type: str | None = None
    
    def register(self, 
                 window_type: str, 
                 window="MainWindow") -> None:
        self.windows[window_type] = window
        if len(self.windows) == 1:
            self.current_type = window_type
        else:
            window.root.withdraw()
    
    def switch_to(self, 
                  window_type: str) -> None:
        if window_type == self.current_type or window_type not in self.windows:
            return
        
        current = self.windows[self.current_type]
        target = self.windows[window_type]
        
        if current.root.winfo_exists():
            x = current.root.winfo_x()
            y = current.root.winfo_y()
            w = current.root.winfo_width()
            h = current.root.winfo_height()
            state = current.root.state()
            
            current.root.withdraw()
            
            target.root.geometry(f"{w}x{h}+{x}+{y}")
            if state == 'zoomed':
                target.root.state('zoomed')
            target.root.deiconify()
            
        self.current_type = window_type
    
    def quit_all(self) -> None:
        for window in list(self.windows.values()):
            if window.root.winfo_exists():
                window._cleanup()
                window.root.destroy()


