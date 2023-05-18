
import sys, traceback, time, math, random, re
import pygame

try:
    WIDTH = 1600     # Ширина игрового окна
    HEIGHT = 720     # Высота игрового окна
    FPS = 60         # Частота кадров в секунду

    SdvigStep = 7    # Скорость призда/уезда
    SdvigFull = 200  # Длина призда/уезда относительно пикселей изначальной картинки (до скейла)

    KoeZon = 0.5     # Множитель ширины захвата зон приезда/уезда: 0-1 
    ZapKoe = 0.7     # Уменьшние ширины запрещенной области на зеркальной части: 0-1
    
    SaveLoki = 0

  # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------    
    print("\n Начали")
      
    try:   # Пробуем взять параметры из файла GameMEX-konfig.txt
        Par = []
        with open("GameMEX-konfig.txt", "r") as fa:
            for line in fa:
                #print(re.sub(r'\s+', " ", line).strip().split(" "))
                Par.append(re.sub(r'\s+', " ", line).strip().split(" ")[0])
 
        if int(Par[0])*int(Par[1])*int(Par[2])*int(Par[3])*int(Par[4]) >= 0 and 0 <= float(Par[5]) <= 1 and 0 <= float(Par[6]) <= 1: 
            WIDTH, HEIGHT, FPS, SdvigStep, SdvigFull, KoeZon, ZapKoe, SaveLoki = int(Par[0]), int(Par[1]), int(Par[2]), int(Par[3]), int(Par[4]), float(Par[5]), float(Par[6]), int(Par[7])        
        else:
            print(" Косяк в конфиге! Беру дефолтные параметры") 
    except: print(" GameMEX-konfig.txt не найден. Беру дефолтные параметры")

  # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------     
    print(f' ширина {WIDTH}\n высота {HEIGHT}\n FPS {FPS}\n скорость приезда {SdvigStep}\n длинна приезда {SdvigFull}\n захват приезда {KoeZon}\n захват зеркальной {ZapKoe}\n сохранять локи {SaveLoki} \n')
    

    #SdvigFull = 1000 # Задать принудильный итоговый сдвиг призда/уезда
    Sdvig = SdvigFull
    ScaleMnoj = HEIGHT / 360  # Множитель скейла фонов
    SdvigFull *= ScaleMnoj  # Итоговый сдвиг призда/уезда по фактическим пикселям на экране
    
    # Пайгеймовские мутки
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("HammerMex")
    clock = pygame.time.Clock()
    
    # ЦВЕТА *Питон поддерживает точку с запятой :)
    BLACK = (0, 0, 0);  WHITE = (255, 255, 255);  RED = (255, 0, 0);  GREEN = (0, 255, 0);  BLUE = (0, 0, 255);  PURP = (68, 56, 80) 

    screen.fill(BLUE)        # Красим сначала синим
    pygame.display.flip()    # Показываем

except Exception as e:       # Перехват ошибки, если что-то забагует
    print("Ошибка начала")
    print(e)
    print()
    print(traceback.format_exc())
    time.sleep(60)

# ==============================================================================================================================================================================
class PLAYER(pygame.sprite.Sprite):     # Класс для меха
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/Meh.png').convert_alpha()
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.image = pygame.transform.scale(self.image, (int(self.size[0]*2), int(self.size[1]*2)))      
        
    def dvi(self, step=2):
        self.rect.x += step
        if self.rect.left > WIDTH:
            self.rect.right = 0
            
class SMOKE(pygame.sprite.Sprite):      # Туманы
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(img).convert_alpha()
        self.size = self.image.get_size()    # Ширина+высота в виде массива [шир, выс]
        self.rect = self.image.get_rect()        
        self.image = pygame.transform.scale(self.image, (WIDTH, int(self.size[1]*ScaleMnoj)))
        self.rect.top = HEIGHT - self.size[1]*ScaleMnoj

class ZADPERED(pygame.sprite.Sprite):   # Однопиксельные фоны на заднем плане и переднем (черная шторка)
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(img).convert_alpha()
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()        
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        
class LOKA(pygame.sprite.Sprite):       # Слои локации
    def __init__(self, img, Paral):
        pygame.sprite.Sprite.__init__(self)      
        self.Paral = Paral
        self.Name = img
        # Неподдающийся понимаю :) замес, который собирает длинную локу с добавлением куска и переворотом
        self.im = pygame.image.load("img/"+img+".png").convert_alpha()
        self.si = self.im.get_size() 
        temp_img = pygame.Surface( (int(self.si[0] + WIDTH/ScaleMnoj + SdvigFull*self.Paral/ScaleMnoj), self.si[1]), pygame.SRCALPHA )        
        temp_img.blit(self.im, (0, 0))
        temp_img.blit(self.im, (self.im.get_size()[0], 0))
        #temp_img.fill(BLACK, (self.im.get_size()[0],0,1,self.im.get_size()[1]))  # Рисовать черную полоску, где кончяается начальная картинка (ее будет иногда видно)           
        self.image = pygame.Surface( (temp_img.get_size()[0]*2, self.si[1]), pygame.SRCALPHA ) 
        self.image.blit(temp_img, (0, 0))
        self.image = pygame.transform.flip(self.image,True,False)
        self.image.blit(temp_img, (0, 0))
        self.image.fill(RED, (temp_img.get_size()[0],0,1,HEIGHT/2))               # Рисовать красную полоску, где разделяются зеркальные части (ее НЕ должно быть видно)
        
        self.Zapreti = []   # массив с запретными зонами, для каждой локи-слоя свой. Сами эти зоны, это будут мини-массивчики из двух значений: [Позия центра, Радиус]
           
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
       
        self.image = pygame.transform.scale(self.image, (int(self.size[0]*ScaleMnoj), int(self.size[1]*ScaleMnoj)))
        
        if SaveLoki == 1: pygame.image.save(self.image, self.Name+"-save.png")  # Сохраняет локу на диск
        
        self.randomize = 0.05   # Множитель от 0 до 1, определяющий положение локации по горизонтали в данный момент
        self.rect.left = int((self.size[0]*ScaleMnoj*-1 + WIDTH) * self.randomize)   # Положение левого края локи-слоя согласно self.randomize
        
        # Переменные для удобства
        self.FinShir   = self.size[0] * ScaleMnoj          # Итоговая ширина слоя-локи после скейла
        self.uniWidth  = self.si[0] * ScaleMnoj            # Ширина уникальной картинки слоя-локи со скейлом (ширина итговой неповторимой ночасти слоя) 
        self.imgDop    = WIDTH + SdvigFull * self.Paral    # Ширина дорисованной зоны
        self.ParKoeZon = SdvigFull * self.Paral * KoeZon   # Ширина добавления к радиусу запретной зоны на приезд/уезд
        
    def update(self):  # Мутки с запретными зонами
        SDVIG = self.rect.left * -1                        # Сдвиг левой стороны экрана от начала картинки слоя
        Center, Radius = SDVIG + WIDTH/2, WIDTH/2 + self.ParKoeZon
        self.Zapreti.append([Center, Radius])                           # Добавление запретной зоны, туда, где ранее был экран
        self.Zapreti.append([self.FinShir-Center, Radius*ZapKoe])       # + в соответствующую точку зеркальной области
        
        # Доп зона в центре, если мы были в начале или в конце слоя
        if (SDVIG < self.imgDop or                       # Случай, когда экран близко к левому ктаю
            SDVIG + WIDTH > self.FinShir - self.imgDop   # Когда экран близко к правому
            ):  
            r1 = self.imgDop - SDVIG   # Считаем радиусы для двух случаев и потом нужно будет выбрать бОльшее значение для итогового радиуса
            r2 = SDVIG + WIDTH - (self.FinShir - self.imgDop)
            Radius = [r1, r2][r1<r2]   # Берем большее значение из r1, r2 (питовская фишка)
            self.Zapreti.append([self.FinShir/2, Radius + self.ParKoeZon])      # + Зона по центру
            
        # Доп зоны в начале и в конце, если мы задели скопированную область в середине локи
        if self.uniWidth - WIDTH - self.ParKoeZon < SDVIG < self.FinShir - self.uniWidth + self.ParKoeZon:  # Питоновская фишка, сразу два сравнеия с "И" Тут SDVIG должен находится в нужном диапазоне
            r1 = SDVIG - (self.uniWidth - WIDTH)
            r2 = self.FinShir - self.uniWidth - SDVIG
            Radius = [r1, r2][r1>r2]   # Берем меньшее значение  
            self.Zapreti.append([0, Radius + self.ParKoeZon])                   # + Зона в начале
            self.Zapreti.append([self.FinShir, Radius + self.ParKoeZon])        # и в конце
        
        while len(self.Zapreti) > 20: self.Zapreti.pop(0)   # Если зон больше нужного, удаляем самую старую из массива
             
        while True:  # Бескончно пробуем          
            for i in range(500):      # Пробуем N раз с текущими зонами 
                self.randomize = random.random()                                      # Кидаем кубик рандома
                self.rect.left = int((self.FinShir - WIDTH) * self.randomize * -1)    # Определяем позицтю слоя
                # Проверяем попадание в центральную часть и по краям в притык
                if (self.rect.left*-1 - int(SdvigFull*self.Paral) <= self.FinShir/2 <= self.rect.left*-1 + WIDTH + int(SdvigFull*self.Paral) or
                    self.rect.left*-1 <= int(SdvigFull*self.Paral) or
                    self.rect.left*-1 >= self.FinShir - WIDTH - int(SdvigFull*self.Paral)
                    ): continue
                
                if self.TestimZoni(): self.Sujaem(); return 1   # Тестим на зоны            
                          
            self.Sujaem() # Cужаем зоны после N попыток
    
    def TestimZoni(self):  # Тестим на пересечение экрана с зонами
        #print(self.rect.left*-1, self.rect.left*-1+WIDTH)
        for Zap in self.Zapreti:
            #print(Zap[0]-Zap[1], Zap[0]+Zap[1])
            if not(self.rect.left*-1+WIDTH < Zap[0]-Zap[1] or self.rect.left*-1 > Zap[0]+Zap[1]): return False
        return True 
        
    def Sujaem(self):      # Сужаем все запретные зоны
        for Zap in self.Zapreti: Zap[1] -= 200       
       
class POLOSA(pygame.sprite.Sprite):     # Клас для полосок-виджетов
    def __init__(self, shir, otniza):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((shir+4, 14))
        self.size = self.image.get_size()
        #self.image.fill((0,0,0))
        #self.image.fill((40,40,40), (2,2,shir,10))
        self.rect = self.image.get_rect()
        
        self.rect.center = (WIDTH/2, HEIGHT-otniza)
        self.rect.left = WIDTH/2-100
        all_sprites.add(self)

def RisPolosa(Pol, Lok):                   # Отрисовка/перерисовка полосок-виджетов (зеленая рамочка, красные области запрета)
    Pol.image.fill((0,0,0));  Pol.image.fill((40,40,40), (2,2,Pol.size[0]-4,10))
    LokRect, Widh, PolWid, Wid = Lok.rect.left/HEIGHT*-10+2, (WIDTH+SdvigFull*Lok.Paral)/HEIGHT*10, Pol.size[0], WIDTH/HEIGHT*10
    Pol.image.fill((30,50,80), (int(PolWid/2)-Widh,2,Widh,10));  Pol.image.fill((35,60,60), (int(PolWid/2),2,Widh,10))
    # Рисуем зеленую рамку
    Pol.image.fill((0,95,0), (LokRect,2,2,10));  Pol.image.fill((0,95,0), (LokRect+Wid-2,2,2,10))
    Pol.image.fill((0,95,0), (LokRect,2,Wid,2));  Pol.image.fill((0,95,0), (LokRect,10,Wid,2))
    # Рисуем запретные зоны
    for Zap in Lok.Zapreti:  # Сами зоны 
        if Zap[1] > 0:       # Только активные (с 0+ шириной)
            left, widh = Zap[0]/HEIGHT*10-Zap[1]/HEIGHT*10, Zap[1]/HEIGHT*10*2
            if left < 0:  widh -= 0-left; left = 0            
            Pol.image.fill((120,20,20), (left+2, 5, widh, 4))

    for Zap in Lok.Zapreti:  # Центры зон    
        Cvet = BLACK         # Активные - красным, неактиыне - черным
        if Zap[1] > 0: Cvet = RED  
        Pol.image.fill(Cvet, (Zap[0]/HEIGHT*10+2, 5, 1, 4))
    
def ff(doub):                              # Плавное замедление или ускорение
    try:    return math.acos(doub) / 1.6
    except: return 0.03                    # В какой-то момент math.acos начинает давать ошибку
        
# ==============================================================================================================================================================================
 
try:
    loka1 = LOKA("loka1", 1)     # Слои локации c их параллаксами
    loka2 = LOKA("loka2", 0.5)
    loka3 = LOKA("loka3", 0.25)
    loka4 = LOKA("loka4", 0.12)   

    zadnik = ZADPERED("img/zadnik.png")       # Самый дальний фон - один пиксель)
    pered  = ZADPERED("img/perednik.png")     # Черная шторка для ухода в темноту - один пиксель)
    pered.image.set_alpha(0)                  # изначально полностью прозрачна
                                            
    smok1 = SMOKE("img/Smoke1.png")           # Задымления - полоска 1 пиксель в ширину PNG24 (с полупрозрачностью)
    smok2 = SMOKE("img/Smoke2.png")
    
    player = PLAYER()  # Мех
    
    
    all_sprites = pygame.sprite.Group()   # Пайгеймовская группа спрайтов    
                                          # спрайты, добавленные в нее позже перекрывают предыдущие
    all_sprites.add(zadnik)
    all_sprites.add(loka4)
    all_sprites.add(loka3)
    all_sprites.add(loka2)
    all_sprites.add(smok2)
    all_sprites.add(loka1)
    all_sprites.add(smok1)
    all_sprites.add(player)
    all_sprites.add(pered)
    
    polosa1 = POLOSA(int(loka1.size[0]/360*10), 15)  # Полоски виджетов
    polosa2 = POLOSA(int(loka2.size[0]/360*10), 31)
    polosa3 = POLOSA(int(loka3.size[0]/360*10), 47)
    polosa4 = POLOSA(int(loka4.size[0]/360*10), 63)
       
    RisPolosa(polosa1, loka1);  RisPolosa(polosa2, loka2);  RisPolosa(polosa3, loka3);  RisPolosa(polosa4, loka4)  # Прописовка полос-виджетов

  # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def PerestavLoka():  # Определяем сдвиги локаций (Селф рандомы) + рисуем виджеты
        tim = time.time()
        all_sprites.update()
        RisPolosa(polosa1, loka1);  RisPolosa(polosa2, loka2);  RisPolosa(polosa3, loka3);  RisPolosa(polosa4, loka4)
        tim = time.time() - tim     
        print("\nЛока переставлена за "+str(int(tim*1000))+" мс")        

  # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 

    # Цикл игры
    running = True
    
    Rejim = 1    # 0-стоим, 1-приезжаем, 2-уезжаем
    Sdvig = 0    
      
    while running:
        clock.tick(FPS)   # Держим цикл на правильной скорости
 
        for event in pygame.event.get():    # Перебор произошедших событий         
            if event.type == pygame.QUIT:   # Обработка крестика окна
                running = False
                
            if event.type == pygame.KEYDOWN:      # Любое нажатие клавы  
                if event.key == pygame.K_SPACE:   # Нажатие пробела
                    PerestavLoka()

                    Sdvig = SdvigFull
                    pered.image.set_alpha(0)
                    
                    #Sdvig = 0
                    #Rejim = 1
                    
                if Rejim == 0 and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):    # Нажатие ентера  
                    print("enter")
                    Rejim = 2
                    Sdvig = 0
                
        # Обновление
        #player.dvi(2)

        if Rejim == 1:  # Прилет
            if Sdvig < SdvigFull: 
                Sdvig += ff(Sdvig/SdvigFull)*SdvigStep   # Движение с замедлением      
                
                loka1.rect.left = (loka1.size[0]*ScaleMnoj*-1 + WIDTH) * loka1.randomize - Sdvig*loka1.Paral + SdvigFull*loka1.Paral
                loka2.rect.left = (loka2.size[0]*ScaleMnoj*-1 + WIDTH) * loka2.randomize - Sdvig*loka2.Paral + SdvigFull*loka2.Paral
                loka3.rect.left = (loka3.size[0]*ScaleMnoj*-1 + WIDTH) * loka3.randomize - Sdvig*loka3.Paral + SdvigFull*loka3.Paral
                loka4.rect.left = (loka4.size[0]*ScaleMnoj*-1 + WIDTH) * loka4.randomize - Sdvig*loka4.Paral + SdvigFull*loka4.Paral           
                
                # Чернота спадает плавно в первую половину полета
                pered.image.set_alpha((1-Sdvig/(SdvigFull/2)) * 255)   # Чернота спадает плавно в первую половину полета
            else: 
                print("Прилетели")
                Rejim = 0
                
        if Rejim == 2:  # Улет 
            if Sdvig < SdvigFull:
                Sdvig += ff(0.95-(Sdvig/SdvigFull))*SdvigStep  # Движение с ускорением
                
                loka1.rect.left = (loka1.size[0]*ScaleMnoj*-1 + WIDTH) * loka1.randomize - Sdvig*loka1.Paral
                loka2.rect.left = (loka2.size[0]*ScaleMnoj*-1 + WIDTH) * loka2.randomize - Sdvig*loka2.Paral
                loka3.rect.left = (loka3.size[0]*ScaleMnoj*-1 + WIDTH) * loka3.randomize - Sdvig*loka3.Paral
                loka4.rect.left = (loka4.size[0]*ScaleMnoj*-1 + WIDTH) * loka4.randomize - Sdvig*loka4.Paral         
                   
                # Чернота наплывает плавно во вторую половину полета
                pered.image.set_alpha(255 - ((1-(Sdvig-SdvigFull/2)/(SdvigFull/2)) * 255)) 
            else: 
                print("Улетели")
                PerestavLoka()    # Переставили локу
                Rejim = 1         # Задали режим прилета
                Sdvig = 0
                
 
        # Рендеринг
        #screen.fill(GREEN)
        all_sprites.draw(screen)

        # После отрисовки всего, "переворачиваем" экран
        pygame.display.flip()

    pygame.quit()
    print("2")    
    time.sleep(0.1)
    
except Exception as e:
   print("Ошибка главного потока")
   print(e)
   print()
   print(traceback.format_exc())
   time.sleep(2)