import pygame
import random
import sys
from heapq import heappush, heappop

# Pygame kütüphanesini başlat
pygame.init()

# Oyun penceresi boyutları ve ızgara ayarları
WIDTH = 800  # Pencere genişliği
HEIGHT = 600  # Pencere yüksekliği
GRID_SIZE = 20  # Izgara hücre boyutu
GRID_WIDTH = WIDTH // GRID_SIZE  # Yatay ızgara sayısı
GRID_HEIGHT = HEIGHT // GRID_SIZE  # Dikey ızgara sayısı

# Oyunda kullanılacak renkler
BLACK = (0, 0, 0)  # Arka plan rengi
WHITE = (255, 255, 255)  # Beyaz renk
RED = (255, 0, 0)  # Yem rengi
GREEN = (0, 255, 0)  # Yeşil yılan rengi
BLUE = (0, 0, 255)  # Mavi yılan rengi
GRAY = (128, 128, 128)  # Duvar rengi

# Oyun penceresini oluştur
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yılan Oyunu - İki Oyunculu")
clock = pygame.time.Clock()  # FPS kontrolü için saat nesnesi

def manhattan_distance(pos1, pos2):
    # İki nokta arasındaki Manhattan mesafesini hesapla
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_neighbors(pos):
    # Bir pozisyonun komşu hücrelerini döndür
    x, y = pos
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Sağ, aşağı, sol, yukarı
        new_x = (x + dx) % GRID_WIDTH
        new_y = (y + dy) % GRID_HEIGHT
        neighbors.append((new_x, new_y))
    return neighbors

def find_path(start, goal, walls, snake_body):
    # A* algoritması ile en kısa yolu bul
    frontier = []
    heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while frontier:
        current = heappop(frontier)[1]
        
        if current == goal:
            break
            
        for next_pos in get_neighbors(current):
            # Duvarlara veya yılan vücuduna çarpma kontrolü
            if next_pos in walls or next_pos in snake_body:
                continue
                
            new_cost = cost_so_far[current] + 1
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + manhattan_distance(goal, next_pos)
                heappush(frontier, (priority, next_pos))
                came_from[next_pos] = current
    
    # Yolu oluştur
    if goal not in came_from:
        return None
        
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    # Yolun güvenli olup olmadığını kontrol et
    # İlk pozisyon hariç yılanın mevcut pozisyonlarıyla çakışmamalı
    for pos in path[1:]:
        if pos in snake_body[:-1]:  # Yılanın kuyruğunun son parçası hariç
            return None
            
    return path

class Wall:
    def __init__(self):
        self.positions = []
        
    def generate_walls(self, snake_positions):
        self.positions = []  # Mevcut duvarları temizle
        attempts = 0  # Deneme sayısı
        max_attempts = 100  # Maksimum deneme sayısı
        
        # 2-4 arası rastgele duvar oluştur
        num_walls = random.randint(2, 4)
        created_walls = 0  # Oluşturulan duvar sayısı
        
        while created_walls < num_walls and attempts < max_attempts:
            # Duvarın başlangıç noktası
            start_x = random.randint(2, GRID_WIDTH-3)
            start_y = random.randint(2, GRID_HEIGHT-3)
            
            # Başlangıç noktası yılanın üzerinde mi kontrol et
            if (start_x, start_y) in snake_positions:
                attempts += 1
                continue
                
            # Duvarın uzunluğu (3-7 arası)
            length = random.randint(3, 7)
            # Yatay veya dikey duvar (0: yatay, 1: dikey)
            is_vertical = random.choice([True, False])
            
            wall_positions = []
            valid_wall = True  # Duvarın geçerli olup olmadığını kontrol et
            
            for i in range(length):
                new_pos = None
                if is_vertical:
                    # Dikey duvar
                    if start_y + i < GRID_HEIGHT - 1:
                        new_pos = (start_x, start_y + i)
                else:
                    # Yatay duvar
                    if start_x + i < GRID_WIDTH - 1:
                        new_pos = (start_x + i, start_y)
                
                if new_pos:
                    # Yeni pozisyon yılanın üzerinde mi kontrol et
                    if new_pos in snake_positions:
                        valid_wall = False
                        break
                    wall_positions.append(new_pos)
            
            if valid_wall and wall_positions:
                self.positions.extend(wall_positions)
                created_walls += 1
            
            attempts += 1

class Snake:
    def __init__(self, start_x, start_y, color):
        # Yılanın başlangıç pozisyonu
        self.positions = [(start_x - i, start_y) for i in range(5)]
        self.direction = (1, 0)  # Başlangıç yönü (sağa doğru)
        self.length = 5  # Başlangıç uzunluğu
        self.path = []  # Yem için izlenecek yol
        self.color = color  # Yılanın rengi
        self.score = 0  # Yılanın skoru
        
    def get_head_position(self):
        # Yılanın baş pozisyonunu döndür
        return self.positions[0]
    
    def update(self, walls, food, other_snake):
        # Yol boşsa veya yem yeni bir konuma taşındıysa yeni yol hesapla
        if not self.path or food.position != self.path[-1]:
            # Yılanın mevcut pozisyonlarını ve diğer yılanın pozisyonlarını engel olarak kullan
            all_obstacles = walls.positions + other_snake.positions
            self.path = find_path(self.get_head_position(), food.position, all_obstacles, self.positions)
            if not self.path:  # Eğer güvenli yol bulunamadıysa
                return False
        
        # Yolun bir sonraki adımına git
        if len(self.path) > 1:
            next_pos = self.path[1]
            current = self.get_head_position()
            
            # Bir sonraki adımın güvenli olduğundan emin ol
            if (next_pos in walls.positions or 
                next_pos in self.positions[:-1] or 
                next_pos in other_snake.positions):
                self.path = []  # Yolu sıfırla ve yeni yol bul
                return True  # Hemen oyunu bitirme, yeni yol bulmayı dene
            
            # Yönü güncelle
            self.direction = ((next_pos[0] - current[0]) % GRID_WIDTH, 
                            (next_pos[1] - current[1]) % GRID_HEIGHT)
            self.path = self.path[1:]  # İlk adımı kaldır
        
        # Yılanın pozisyonunu güncelle
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        
        # Son güvenlik kontrolü
        if (new in self.positions[:-1] or 
            new in walls.positions or 
            new in other_snake.positions):
            return False
            
        # Yeni pozisyonu listeye ekle
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()  # Fazla uzunluğu kes
        return True
    
    def reset(self, start_x, start_y):
        # Oyun yeniden başlatıldığında yılanı sıfırla
        self.positions = [(start_x - i, start_y) for i in range(5)]
        self.direction = (1, 0)
        self.length = 5
        self.path = []
        self.score = 0

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position([], [])
        
    def randomize_position(self, wall_positions, snake_positions):
        # Yem için rastgele pozisyon belirle (duvarların ve yılanın olmadığı bir yerde)
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            pos = (random.randint(0, GRID_WIDTH-1),
                  random.randint(0, GRID_HEIGHT-1))
            if pos not in wall_positions and pos not in snake_positions:
                self.position = pos
                return True
            attempts += 1
        
        # Eğer uygun pozisyon bulunamazsa, en son bulunan pozisyonu kullan
        return False

def main():
    # İki yılan oluştur (biri sol tarafta, diğeri sağ tarafta)
    snake1 = Snake(GRID_WIDTH // 4, GRID_HEIGHT // 2, GREEN)  # Yeşil yılan
    snake2 = Snake(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2, BLUE)  # Mavi yılan
    food = Food()    # Yem nesnesini oluştur
    walls = Wall()   # Duvar nesnesini oluştur
    food_counter = 0 # Yenilen yem sayacı
    game_over = False  # Oyun durumu
    winner = None    # Kazanan yılan
    
    # Ana oyun döngüsü
    while True:
        # Kullanıcı girdilerini kontrol et
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Oyun bittiyse SPACE tuşu ile yeniden başlat
                if game_over and event.key == pygame.K_SPACE:
                    snake1.reset(GRID_WIDTH // 4, GRID_HEIGHT // 2)
                    snake2.reset(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2)
                    walls = Wall()
                    food_counter = 0
                    game_over = False
                    winner = None
                    # Yeni yem pozisyonu belirle
                    food.randomize_position(walls.positions, snake1.positions + snake2.positions)
        
        if not game_over:
            # Yılanların pozisyonlarını güncelle
            if not snake1.update(walls, food, snake2):
                game_over = True
                winner = snake2
            elif not snake2.update(walls, food, snake1):
                game_over = True
                winner = snake1
            
            # Yem yendi mi kontrol et
            head1 = snake1.get_head_position()
            head2 = snake2.get_head_position()
            
            if head1 == food.position or head2 == food.position:
                # Hangi yılan yemi yedi?
                if head1 == food.position:
                    snake1.length += 1
                    snake1.score += 10
                else:
                    snake2.length += 1
                    snake2.score += 10
                
                food_counter += 1
                
                # Her 3 yemde bir yeni duvarlar oluştur
                if food_counter % 3 == 0:
                    walls.generate_walls(snake1.positions + snake2.positions)
                
                # Yeni yem pozisyonu belirle
                if not food.randomize_position(walls.positions, snake1.positions + snake2.positions):
                    game_over = True
                    # Skoru yüksek olan kazanır
                    winner = snake1 if snake1.score > snake2.score else snake2
            
            # Yılanlar çarpıştı mı?
            if head1 == head2:
                game_over = True
                # Uzunluğu fazla olan kazanır
                winner = snake1 if snake1.length > snake2.length else snake2
        
        # Ekranı temizle
        screen.fill(BLACK)
        
        # Duvarları çiz
        for pos in walls.positions:
            pygame.draw.rect(screen, GRAY,
                           (pos[0]*GRID_SIZE, pos[1]*GRID_SIZE,
                            GRID_SIZE-2, GRID_SIZE-2))
        
        # Yılanları çiz
        for pos in snake1.positions:
            pygame.draw.rect(screen, snake1.color,
                           (pos[0]*GRID_SIZE, pos[1]*GRID_SIZE,
                            GRID_SIZE-2, GRID_SIZE-2))
        
        for pos in snake2.positions:
            pygame.draw.rect(screen, snake2.color,
                           (pos[0]*GRID_SIZE, pos[1]*GRID_SIZE,
                            GRID_SIZE-2, GRID_SIZE-2))
        
        # Yemi çiz
        pygame.draw.rect(screen, RED,
                        (food.position[0]*GRID_SIZE, food.position[1]*GRID_SIZE,
                         GRID_SIZE-2, GRID_SIZE-2))
        
        # Skorları göster
        font = pygame.font.Font(None, 36)
        score1_text = font.render(f'Yeşil: {snake1.score}', True, GREEN)
        score2_text = font.render(f'Mavi: {snake2.score}', True, BLUE)
        screen.blit(score1_text, (10, 10))
        screen.blit(score2_text, (WIDTH - 120, 10))
        
        # Oyun bitti mesajını göster
        if game_over:
            if winner:
                winner_color = "Yeşil" if winner.color == GREEN else "Mavi"
                game_over_text = font.render(f'{winner_color} Yılan Kazandı! Tekrar başlamak için SPACE', True, WHITE)
            else:
                game_over_text = font.render('Berabere! Tekrar başlamak için SPACE', True, WHITE)
            screen.blit(game_over_text, (WIDTH//4, HEIGHT//2))
        
        # Ekranı güncelle
        pygame.display.flip()
        clock.tick(10)  # Oyun hızını 10 FPS olarak ayarla

if __name__ == "__main__":
    main()
