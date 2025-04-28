import pygame
import pygame.gfxdraw
import json
import math
from typing import List, Dict, Tuple, Optional, Union

pygame.init()

DEFAULT_WIDTH, DEFAULT_HEIGHT = 800, 600
MIN_WINDOW_SIZE = (400, 300)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (200, 200, 200)
COLOR_LIGHT_GRAY = (230, 230, 230)
COLOR_DARK_GRAY = (100, 100, 100)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_PURPLE = (128, 0, 128)
BUTTON_HEIGHT = 30
PADDING = 10
SHAPE_TYPES = ["rectangle", "circle", "ellipse", "line", "polygon", "arc"]
TOOLBAR_WIDTH = 200

class Shape:
    def __init__(self, shape_type: str, color: Tuple[int, int, int], points: List[Tuple[int, int]], 
                 width: int = 0, filled: bool = True, rotation: int = 0):
        self.shape_type = shape_type
        self.color = color
        self.points = points
        self.width = width
        self.filled = filled
        self.rotation = rotation
        self.selected = False
        self.dragging = False
        self.resize_handle = None
        self.original_points = points.copy()

    def draw(self, surface: pygame.Surface):
        if self.shape_type == "rectangle":
            if self.filled:
                pygame.draw.rect(surface, self.color, self.get_rect(), 0)
            else:
                pygame.draw.rect(surface, self.color, self.get_rect(), self.width)
        elif self.shape_type == "circle":
            if self.filled:
                pygame.draw.circle(surface, self.color, self.points[0], self.points[1][0])
            else:
                pygame.draw.circle(surface, self.color, self.points[0], self.points[1][0], self.width)
        elif self.shape_type == "ellipse":
            if self.filled:
                pygame.draw.ellipse(surface, self.color, self.get_rect(), 0)
            else:
                pygame.draw.ellipse(surface, self.color, self.get_rect(), self.width)
        elif self.shape_type == "line":
            pygame.draw.line(surface, self.color, self.points[0], self.points[1], self.width)
        elif self.shape_type == "polygon":
            if len(self.points) >= 3:
                if self.filled:
                    pygame.draw.polygon(surface, self.color, self.points, 0)
                else:
                    pygame.draw.polygon(surface, self.color, self.points, self.width)
        elif self.shape_type == "arc":
            pygame.draw.arc(surface, self.color, self.get_rect(), self.points[2], self.points[3], self.width)
        
        if self.selected:
            rect = self.get_rect()
            pygame.draw.rect(surface, COLOR_RED, rect, 1)
            
            handles = [
                (rect.left, rect.top), (rect.centerx, rect.top), (rect.right, rect.top),
                (rect.left, rect.centery), (rect.right, rect.centery),
                (rect.left, rect.bottom), (rect.centerx, rect.bottom), (rect.right, rect.bottom)
            ]
            
            for handle in handles:
                pygame.draw.circle(surface, COLOR_RED, handle, 4)
    
    def get_rect(self) -> pygame.Rect:
        if self.shape_type in ["rectangle", "ellipse", "arc"]:
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        elif self.shape_type == "circle":
            center, radius = self.points
            return pygame.Rect(center[0] - radius[0], center[1] - radius[0], radius[0] * 2, radius[0] * 2)
        elif self.shape_type == "line":
            return pygame.Rect(self.points[0][0], self.points[0][1], 
                             self.points[1][0] - self.points[0][0], 
                             self.points[1][1] - self.points[0][1])
        elif self.shape_type == "polygon":
            min_x = min(p[0] for p in self.points)
            min_y = min(p[1] for p in self.points)
            max_x = max(p[0] for p in self.points)
            max_y = max(p[1] for p in self.points)
            return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        return pygame.Rect(0, 0, 0, 0)
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        if self.shape_type == "rectangle":
            return self.get_rect().collidepoint(point)
        elif self.shape_type == "circle":
            center, radius = self.points
            distance = math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2)
            return distance <= radius[0]
        elif self.shape_type == "ellipse":
            return self.get_rect().collidepoint(point)
        elif self.shape_type == "line":
            rect = pygame.Rect(
                min(self.points[0][0], self.points[1][0]) - self.width,
                min(self.points[0][1], self.points[1][1]) - self.width,
                abs(self.points[1][0] - self.points[0][0]) + self.width * 2,
                abs(self.points[1][1] - self.points[0][1]) + self.width * 2
            )
            return rect.collidepoint(point)
        elif self.shape_type == "polygon":
            return point_in_polygon(point, self.points)
        elif self.shape_type == "arc":
            return self.get_rect().collidepoint(point)
        return False
    
    def get_resize_handle_at_point(self, point: Tuple[int, int]) -> Optional[int]:
        if not self.selected:
            return None
        
        rect = self.get_rect()
        handles = [
            (rect.left, rect.top), (rect.centerx, rect.top), (rect.right, rect.top),
            (rect.left, rect.centery), (rect.right, rect.centery),
            (rect.left, rect.bottom), (rect.centerx, rect.bottom), (rect.right, rect.bottom)
        ]
        
        for i, handle in enumerate(handles):
            if math.sqrt((point[0] - handle[0])**2 + (point[1] - handle[1])**2) <= 6:
                return i
        return None
    
    def move(self, dx: int, dy: int):
        if self.shape_type == "circle":
            self.points[0] = (self.points[0][0] + dx, self.points[0][1] + dy)
        elif self.shape_type == "polygon":
            self.points = [(p[0] + dx, p[1] + dy) for p in self.points]
        else:
            new_points = []
            for p in self.points:
                if isinstance(p, tuple):
                    new_points.append((p[0] + dx, p[1] + dy))
                else:
                    new_points.append(p)
            self.points = new_points
    
    def resize(self, handle_index: int, dx: int, dy: int):
        rect = self.get_rect()
        
        if self.shape_type in ["rectangle", "ellipse", "arc"]:
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            
            if handle_index == 0:
                self.points[0] = (x1 + dx, y1 + dy)
            elif handle_index == 1:
                self.points[0] = (x1, y1 + dy)
            elif handle_index == 2:
                self.points[1] = (x2 + dx, y1 + dy)
            elif handle_index == 3:
                self.points[0] = (x1 + dx, y1)
            elif handle_index == 4:
                self.points[1] = (x2 + dx, y2)
            elif handle_index == 5:
                self.points[0] = (x1 + dx, y2 + dy)
            elif handle_index == 6:
                self.points[1] = (x2, y2 + dy)
            elif handle_index == 7:
                self.points[1] = (x2 + dx, y2 + dy)
        
        elif self.shape_type == "circle":
            center, radius = self.points
            if handle_index in [2, 4, 7]:
                radius = (radius[0] + dx,)
            elif handle_index in [0, 3, 5]:
                radius = (radius[0] - dx,)
            elif handle_index in [1, 6]:
                radius = (radius[0] + dy,)
            self.points[1] = radius
        
        elif self.shape_type == "line":
            if handle_index == 0:
                self.points[0] = (self.points[0][0] + dx, self.points[0][1] + dy)
            elif handle_index == 7:
                self.points[1] = (self.points[1][0] + dx, self.points[1][1] + dy)
        
        elif self.shape_type == "polygon":
            center_x = sum(p[0] for p in self.points) / len(self.points)
            center_y = sum(p[1] for p in self.points) / len(self.points)
            
            for i, (x, y) in enumerate(self.points):
                dir_x = x - center_x
                dir_y = y - center_y
                
                if abs(dir_x) > 5 or abs(dir_y) > 5:
                    if handle_index in [2, 4, 7]:
                        if dir_x > 0:
                            self.points[i] = (x + dx, y)
                    elif handle_index in [0, 3, 5]:
                        if dir_x < 0:
                            self.points[i] = (x + dx, y)
                    elif handle_index in [1, 6]:
                        if dir_y < 0 or dir_y > 0:
                            self.points[i] = (x, y + dy)

def point_in_polygon(point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int] = COLOR_GRAY, 
                 hover_color: Tuple[int, int, int] = COLOR_LIGHT_GRAY,
                 text_color: Tuple[int, int, int] = COLOR_BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def draw(self, surface: pygame.Surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, COLOR_BLACK, self.rect, 1)
        
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos: Tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos: Tuple[int, int], event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.rect.collidepoint(pos)
        return False

class ColorPicker:
    def __init__(self, x: int, y: int, width: int, height: int, initial_color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = initial_color
        self.colors = [
            COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW, COLOR_PURPLE,
            (255, 165, 0), (0, 255, 255), (255, 0, 255), (128, 0, 0),
            (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128),
            (0, 128, 128), (192, 192, 192), (128, 128, 128), COLOR_BLACK
        ]
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, COLOR_WHITE, self.rect)
        pygame.draw.rect(surface, COLOR_BLACK, self.rect, 1)
        
        color_size = 20
        cols = self.rect.width // color_size
        for i, color in enumerate(self.colors):
            row = i // cols
            col = i % cols
            color_rect = pygame.Rect(
                self.rect.x + col * color_size,
                self.rect.y + row * color_size,
                color_size, color_size
            )
            pygame.draw.rect(surface, color, color_rect)
            pygame.draw.rect(surface, COLOR_BLACK, color_rect, 1)
            
            if color == self.color:
                pygame.draw.rect(surface, COLOR_WHITE, color_rect, 3)
    
    def get_color_at_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int, int]]:
        if not self.rect.collidepoint(pos):
            return None
        
        color_size = 20
        cols = self.rect.width // color_size
        x, y = pos[0] - self.rect.x, pos[1] - self.rect.y
        col = x // color_size
        row = y // color_size
        index = row * cols + col
        
        if 0 <= index < len(self.colors):
            return self.colors[index]
        return None

class PygameCalculator:
    def __init__(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
        self.width = max(width, MIN_WINDOW_SIZE[0])
        self.height = max(height, MIN_WINDOW_SIZE[1])
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.show_grid = False
        pygame.display.set_caption("Pygame Calculator")
        
        self.drawing_area = pygame.Rect(TOOLBAR_WIDTH, 0, self.width - TOOLBAR_WIDTH, self.height)
        
        self.shapes: List[Shape] = []
        self.selected_shape: Optional[Shape] = None
        self.current_shape: Optional[Shape] = None
        self.current_shape_type = "rectangle"
        self.current_color = COLOR_RED
        self.current_width = 2
        self.filled = True
        
        self.drawing = False
        self.moving = False
        self.resizing = False
        self.last_pos = (0, 0)
        
        self.create_ui_elements()
        
        self.grid_size = 20
        self.show_grid = True
    
    def create_ui_elements(self):
        self.shape_buttons = []
        for i, shape_type in enumerate(SHAPE_TYPES):
            btn = Button(
                PADDING, 
                PADDING + i * (BUTTON_HEIGHT + PADDING), 
                TOOLBAR_WIDTH - 2 * PADDING, 
                BUTTON_HEIGHT, 
                shape_type.capitalize()
            )
            self.shape_buttons.append(btn)
        
        self.color_picker = ColorPicker(
            PADDING, 
            PADDING + len(SHAPE_TYPES) * (BUTTON_HEIGHT + PADDING), 
            TOOLBAR_WIDTH - 2 * PADDING, 
            120, 
            self.current_color
        )
        
        self.width_label_rect = pygame.Rect(
            PADDING,
            self.color_picker.rect.bottom + PADDING,
            TOOLBAR_WIDTH - 2 * PADDING,
            20
        )
        
        self.width_slider = pygame.Rect(
            PADDING,
            self.width_label_rect.bottom + PADDING,
            TOOLBAR_WIDTH - 2 * PADDING,
            20
        )
        
        self.fill_button = Button(
            PADDING,
            self.width_slider.bottom + PADDING,
            TOOLBAR_WIDTH - 2 * PADDING,
            BUTTON_HEIGHT,
            "Filled: Yes",
            COLOR_GREEN if self.filled else COLOR_RED
        )
        
        self.grid_button = Button(
            PADDING,
            self.fill_button.rect.bottom + PADDING,
            TOOLBAR_WIDTH - 2 * PADDING,
            BUTTON_HEIGHT,
            "Grid: On",
            COLOR_GREEN if self.show_grid else COLOR_RED
        )
        
        self.clear_button = Button(
            PADDING,
            self.grid_button.rect.bottom + PADDING,
            TOOLBAR_WIDTH - 2 * PADDING,
            BUTTON_HEIGHT,
            "Clear All",
            (255, 100, 100))
        
        self.generate_button = Button(
            PADDING,
            self.height - BUTTON_HEIGHT - PADDING,
            TOOLBAR_WIDTH - 2 * PADDING,
            BUTTON_HEIGHT,
            "Generate Code",
            (100, 255, 100))
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_in_drawing_area = self.drawing_area.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_left_click(mouse_pos, mouse_in_drawing_area)
                elif event.button == 3 and self.drawing and self.current_shape_type == "polygon":
                    if len(self.current_shape.points) >= 3:
                        self.shapes.append(self.current_shape)
                        self.current_shape = None
                        self.drawing = False
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.handle_left_click_release(mouse_pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(mouse_pos, mouse_in_drawing_area)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE and self.selected_shape:
                    self.shapes.remove(self.selected_shape)
                    self.selected_shape = None
                elif event.key == pygame.K_RETURN and self.drawing and self.current_shape_type == "polygon":
                    if len(self.current_shape.points) >= 3:
                        self.shapes.append(self.current_shape)
                        self.current_shape = None
                        self.drawing = False
        
        return True
    
    def handle_resize(self, event):
        new_width = max(event.w, MIN_WINDOW_SIZE[0])
        new_height = max(event.h, MIN_WINDOW_SIZE[1])
        self.width, self.height = new_width, new_height
        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
        self.drawing_area.width = new_width - TOOLBAR_WIDTH
        self.drawing_area.height = new_height
        self.generate_button.rect.y = new_height - BUTTON_HEIGHT - PADDING
    
    def handle_left_click_release(self, mouse_pos):
        if self.moving and self.selected_shape:
            self.selected_shape.dragging = False
            self.moving = False
        
        if self.resizing and self.selected_shape:
            self.selected_shape.resize_handle = None
            self.resizing = False
        
        if self.drawing and self.current_shape and self.current_shape_type != "polygon":
            self.shapes.append(self.current_shape)
            self.current_shape = None
            self.drawing = False
    
    def handle_left_click(self, mouse_pos, mouse_in_drawing_area):
        if mouse_pos[0] < TOOLBAR_WIDTH:
            self.handle_toolbar_click(mouse_pos)
            return
        
        clicked_shape = None
        for shape in reversed(self.shapes):
            if shape.contains_point(mouse_pos):
                clicked_shape = shape
                break
        
        if clicked_shape:
            for shape in self.shapes:
                shape.selected = False
            
            clicked_shape.selected = True
            self.selected_shape = clicked_shape
            
            handle_index = clicked_shape.get_resize_handle_at_point(mouse_pos)
            if handle_index is not None:
                clicked_shape.resize_handle = handle_index
                self.resizing = True
            else:
                self.moving = True
                clicked_shape.dragging = True
            
            self.last_pos = mouse_pos
        else:
            if mouse_in_drawing_area:
                if self.drawing and self.current_shape and self.current_shape_type == "polygon":
                    self.current_shape.points.append(mouse_pos)
                else:
                    self.deselect_all_shapes()
                    self.start_new_shape(mouse_pos)
    
    def handle_toolbar_click(self, mouse_pos):
        mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': mouse_pos})
        
        for i, button in enumerate(self.shape_buttons):
            if button.is_clicked(mouse_pos, mouse_event):
                self.current_shape_type = SHAPE_TYPES[i]
                return
        
        new_color = self.color_picker.get_color_at_pos(mouse_pos)
        if new_color:
            self.current_color = new_color
            return
        
        if self.fill_button.is_clicked(mouse_pos, mouse_event):
            self.filled = not self.filled
            self.fill_button.text = f"Filled: {'Yes' if self.filled else 'No'}"
            self.fill_button.color = COLOR_GREEN if self.filled else COLOR_RED
            return
        
        if self.grid_button.is_clicked(mouse_pos, mouse_event):
            self.show_grid = not self.show_grid
            self.grid_button.text = f"Grid: {'On' if self.show_grid else 'Off'}"
            self.grid_button.color = COLOR_GREEN if self.show_grid else COLOR_RED
            return
        
        if self.clear_button.is_clicked(mouse_pos, mouse_event):
            self.shapes = []
            self.selected_shape = None
            self.current_shape = None
            return
        
        if self.generate_button.is_clicked(mouse_pos, mouse_event):
            self.generate_pygame_code()
            return
        
        if self.width_slider.collidepoint(mouse_pos):
            rel_x = mouse_pos[0] - self.width_slider.x
            self.current_width = max(1, min(20, rel_x // 10))
    
    def handle_mouse_motion(self, mouse_pos, mouse_in_drawing_area):
        for button in self.shape_buttons:
            button.check_hover(mouse_pos)
        self.fill_button.check_hover(mouse_pos)
        self.grid_button.check_hover(mouse_pos)
        self.clear_button.check_hover(mouse_pos)
        self.generate_button.check_hover(mouse_pos)
        
        dx = mouse_pos[0] - self.last_pos[0]
        dy = mouse_pos[1] - self.last_pos[1]
        
        if self.moving and self.selected_shape and self.selected_shape.dragging:
            self.selected_shape.move(dx, dy)
        
        elif self.resizing and self.selected_shape and self.selected_shape.resize_handle is not None:
            self.selected_shape.resize(self.selected_shape.resize_handle, dx, dy)
        
        elif self.drawing and self.current_shape and mouse_in_drawing_area:
            if self.current_shape_type in ["rectangle", "ellipse", "arc"]:
                self.current_shape.points[1] = mouse_pos
            elif self.current_shape_type == "circle":
                radius = int(math.sqrt((mouse_pos[0] - self.current_shape.points[0][0])**2 + 
                            (mouse_pos[1] - self.current_shape.points[0][1])**2))
                self.current_shape.points[1] = (radius,)
            elif self.current_shape_type == "line":
                self.current_shape.points[1] = mouse_pos
        
        self.last_pos = mouse_pos
    
    def start_new_shape(self, pos):
        if self.current_shape_type in ["rectangle", "ellipse", "arc"]:
            self.current_shape = Shape(
                self.current_shape_type,
                self.current_color,
                [pos, pos],
                self.current_width,
                self.filled
            )
            if self.current_shape_type == "arc":
                self.current_shape.points.extend([0, math.pi])
        elif self.current_shape_type == "circle":
            self.current_shape = Shape(
                "circle",
                self.current_color,
                [pos, (10,)],
                self.current_width,
                self.filled
            )
        elif self.current_shape_type == "line":
            self.current_shape = Shape(
                "line",
                self.current_color,
                [pos, pos],
                self.current_width,
                False
            )
        elif self.current_shape_type == "polygon":
            self.current_shape = Shape(
                "polygon",
                self.current_color,
                [pos],
                self.current_width,
                self.filled
            )
        
        self.drawing = True
    
    def deselect_all_shapes(self):
        for shape in self.shapes:
            shape.selected = False
        self.selected_shape = None
    
    def draw_grid(self, surface):
        if not self.show_grid:
            return
        
        for x in range(self.drawing_area.left, self.drawing_area.right, self.grid_size):
            pygame.draw.line(surface, COLOR_LIGHT_GRAY, (x, self.drawing_area.top), 
                            (x, self.drawing_area.bottom), 1)
        
        for y in range(self.drawing_area.top, self.drawing_area.bottom, self.grid_size):
            pygame.draw.line(surface, COLOR_LIGHT_GRAY, (self.drawing_area.left, y), 
                            (self.drawing_area.right, y), 1)
    
    def draw_ui(self):
        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, (0, 0, TOOLBAR_WIDTH, self.height))
        
        for button in self.shape_buttons:
            button.draw(self.screen)
            if SHAPE_TYPES[self.shape_buttons.index(button)] == self.current_shape_type:
                pygame.draw.rect(self.screen, COLOR_YELLOW, button.rect, 3)
        
        self.color_picker.draw(self.screen)
        
        pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, self.width_slider)
        pygame.draw.rect(self.screen, COLOR_BLACK, self.width_slider, 1)
        
        indicator_x = self.width_slider.x + self.current_width * 10
        indicator_rect = pygame.Rect(
            indicator_x - 5,
            self.width_slider.y - 5,
            10,
            self.width_slider.height + 10
        )
        pygame.draw.rect(self.screen, COLOR_BLUE, indicator_rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, indicator_rect, 1)
        
        font = pygame.font.SysFont(None, 24)
        label = font.render(f"Width: {self.current_width}", True, COLOR_WHITE)
        self.screen.blit(label, (self.width_label_rect.x, self.width_label_rect.y))
        
        self.fill_button.draw(self.screen)
        self.grid_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.generate_button.draw(self.screen)
    
    def draw_shapes(self):
        self.draw_grid(self.screen)
        
        for shape in self.shapes:
            shape.draw(self.screen)
        
        if self.current_shape:
            self.current_shape.draw(self.screen)
    
    def generate_pygame_code(self):
        code = """import pygame
import sys

pygame.init()

SCREEN_WIDTH = {width}
SCREEN_HEIGHT = {height}
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Generated Drawing")

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
""".format(width=self.drawing_area.width, height=self.drawing_area.height)

        code += "\ndef draw_shapes(surface):\n"
        code += "    surface.fill(COLOR_WHITE)\n"
        
        for i, shape in enumerate(self.shapes):
            if shape.shape_type == "rectangle":
                rect = shape.get_rect()
                if shape.filled:
                    code += f"    pygame.draw.rect(surface, {shape.color}, pygame.Rect({rect.x}, {rect.y}, {rect.width}, {rect.height}), 0)\n"
                else:
                    code += f"    pygame.draw.rect(surface, {shape.color}, pygame.Rect({rect.x}, {rect.y}, {rect.width}, {rect.height}), {shape.width})\n"
            
            elif shape.shape_type == "circle":
                center = shape.points[0]
                radius = shape.points[1][0]
                if shape.filled:
                    code += f"    pygame.draw.circle(surface, {shape.color}, ({center[0]}, {center[1]}), {radius}, 0)\n"
                else:
                    code += f"    pygame.draw.circle(surface, {shape.color}, ({center[0]}, {center[1]}), {radius}, {shape.width})\n"
            
            elif shape.shape_type == "ellipse":
                rect = shape.get_rect()
                if shape.filled:
                    code += f"    pygame.draw.ellipse(surface, {shape.color}, pygame.Rect({rect.x}, {rect.y}, {rect.width}, {rect.height}), 0)\n"
                else:
                    code += f"    pygame.draw.ellipse(surface, {shape.color}, pygame.Rect({rect.x}, {rect.y}, {rect.width}, {rect.height}), {shape.width})\n"
            
            elif shape.shape_type == "line":
                p1, p2 = shape.points
                code += f"    pygame.draw.line(surface, {shape.color}, ({p1[0]}, {p1[1]}), ({p2[0]}, {p2[1]}), {shape.width})\n"
            
            elif shape.shape_type == "polygon":
                points = ", ".join(f"({p[0]}, {p[1]})" for p in shape.points)
                if shape.filled:
                    code += f"    pygame.draw.polygon(surface, {shape.color}, [{points}], 0)\n"
                else:
                    code += f"    pygame.draw.polygon(surface, {shape.color}, [{points}], {shape.width})\n"
            
            elif shape.shape_type == "arc":
                rect = shape.get_rect()
                start_angle, end_angle = shape.points[2], shape.points[3]
                code += f"    pygame.draw.arc(surface, {shape.color}, pygame.Rect({rect.x}, {rect.y}, {rect.width}, {rect.height}), {start_angle}, {end_angle}, {shape.width})\n"
        
        code += """
def main():
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        draw_shapes(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
"""

        with open("generated_drawing.py", "w") as f:
            f.write(code)
        
        font = pygame.font.SysFont(None, 36)
        message = font.render("Code saved to generated_drawing.py", True, COLOR_GREEN)
        message_rect = message.get_rect(center=(self.width // 2, self.height - 50))
        
        self.screen.blit(message, message_rect)
        pygame.display.flip()
        pygame.time.delay(2000)
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            
            self.screen.fill(COLOR_WHITE)
            
            self.draw_shapes()
            self.draw_ui()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    app = PygameCalculator(DEFAULT_WIDTH, DEFAULT_HEIGHT)
    app.run()