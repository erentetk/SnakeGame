import pygame
import random
import sys

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
GREEN = (0, 255, 0)  # Yılan rengi
GRAY = (128, 128, 128)  # Duvar rengi

# Oyun penceresini oluştur
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yılan Oyunu")
clock = pygame.time.Clock()  # FPS kontrolü için saat nesnesi

class Wall:
    def __init__(self):
        self.positions = []
        
    def generate_walls(self):
        self.positions = []  # Mevcut duvarları temizle
        # 2-4 arası rastgele duvar oluştur
        num_walls = random.randint(2, 4)
        for _ in range(num_walls):
            # Duvarın başlangıç noktası
            start_x = random.randint(2, GRID_WIDTH-3)
            start_y = random.randint(2, GRID_HEIGHT-3)
            # Duvarın uzunluğu (3-7 arası)
            length = random.randint(3, 7)
            # Yatay veya dikey duvar (0: yatay, 1: dikey)
            is_vertical = random.choice([True, False])
            
            wall_positions = []
            for i in range(length):
                if is_vertical:
                    # Dikey duvar
                    if start_y + i < GRID_HEIGHT - 1:
                        wall_positions.append((start_x, start_y + i))
                else:
                    # Yatay duvar
                    if start_x + i < GRID_WIDTH - 1:
                        wall_positions.append((start_x + i, start_y))
            
            self.positions.extend(wall_positions)

class Snake:
    def __init__(self):
        # Yılanın başlangıç pozisyonu (ekranın ortası)
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        # Başlangıçta 5 birimlik yılan oluştur (sola doğru uzanan)
        self.positions = [(start_x - i, start_y) for i in range(5)]
        self.direction = (1, 0)  # Başlangıç yönü (sağa doğru)
        self.length = 5  # Başlangıç uzunluğu
        
    def get_head_position(self):
        # Yılanın baş pozisyonunu döndür
        return self.positions[0]
    
    def update(self, walls):
        # Yılanın pozisyonunu güncelle
        cur = self.get_head_position()
        x, y = self.direction
        # Yeni baş pozisyonu (ekran sınırlarını aşınca karşı taraftan çıkar)
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        
        # Yılan kendine çarptı mı veya duvara çarptı mı kontrol et
        if new in self.positions[3:] or new in walls.positions:
            return False
            
        # Yeni pozisyonu listeye ekle
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()  # Fazla uzunluğu kes
        return True
    
    def reset(self):
        # Oyun yeniden başlatıldığında yılanı sıfırla
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        # Başlangıçta 5 birimlik yılan oluştur (sola doğru uzanan)
        self.positions = [(start_x - i, start_y) for i in range(5)]
        self.direction = (1, 0)
        self.length = 5

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position([])
        
    def randomize_position(self, wall_positions):
        # Yem için rastgele pozisyon belirle (duvarların olmadığı bir yerde)
        while True:
            pos = (random.randint(0, GRID_WIDTH-1),
                  random.randint(0, GRID_HEIGHT-1))
            if pos not in wall_positions:
                self.position = pos
                break

def main():
    snake = Snake()  # Yılan nesnesini oluştur
    food = Food()    # Yem nesnesini oluştur
    walls = Wall()   # Duvar nesnesini oluştur
    score = 0        # Skor sayacı
    food_counter = 0 # Yenilen yem sayacı
    game_over = False  # Oyun durumu
    
    # Ana oyun döngüsü
    while True:
        # Kullanıcı girdilerini kontrol et
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Oyun bittiyse SPACE tuşu ile yeniden başlat
                if game_over:
                    if event.key == pygame.K_SPACE:
                        snake.reset()
                        walls = Wall()
                        food_counter = 0
                        score = 0
                        game_over = False
                        continue
                
                # Yön tuşları kontrolü
                if event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)
        
        if not game_over:
            # Yılanın pozisyonunu güncelle
            if not snake.update(walls):
                game_over = True
            
            # Yem yendi mi kontrol et
            if snake.get_head_position() == food.position:
                snake.length += 1  # Yılanı büyüt
                score += 10        # Skoru artır
                food_counter += 1  # Yem sayacını artır
                
                # Her 3 yemde bir yeni duvarlar oluştur
                if food_counter % 3 == 0:
                    walls.generate_walls()
                
                # Yeni yem pozisyonu belirle
                food.randomize_position(walls.positions)
        
        # Ekranı temizle
        screen.fill(BLACK)
        
        # Duvarları çiz
        for pos in walls.positions:
            pygame.draw.rect(screen, GRAY,
                           (pos[0]*GRID_SIZE, pos[1]*GRID_SIZE,
                            GRID_SIZE-2, GRID_SIZE-2))
        
        # Yılanı çiz
        for pos in snake.positions:
            pygame.draw.rect(screen, GREEN,
                           (pos[0]*GRID_SIZE, pos[1]*GRID_SIZE,
                            GRID_SIZE-2, GRID_SIZE-2))
        
        # Yemi çiz
        pygame.draw.rect(screen, RED,
                        (food.position[0]*GRID_SIZE, food.position[1]*GRID_SIZE,
                         GRID_SIZE-2, GRID_SIZE-2))
        
        # Skoru göster
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Skor: {score}', True, RED)
        screen.blit(score_text, (10, 10))
        
        # Oyun bitti mesajını göster
        if game_over:
            game_over_text = font.render('Oyun Bitti! Tekrar başlamak için SPACE', True, WHITE)
            screen.blit(game_over_text, (WIDTH//4, HEIGHT//2))
        
        # Ekranı güncelle
        pygame.display.flip()
        clock.tick(10)  # Oyun hızını 10 FPS olarak ayarla

if __name__ == "__main__":
    main()
