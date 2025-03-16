import pygame
import sys
import random
from pygame.locals import *

# 초기화
pygame.init()  # pygame의 모든 모듈 초기화
pygame.mixer.init()  # mixer 초기화

# 화면 설정
screen_width, screen_height = 1200, 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Accendio")

# 배경음악 로드 및 재생 설정
background_music = pygame.mixer.Sound("Accendio.mp3")
background_music.play(-1)  # -1은 무한 반복을 의미

# 색상 정의
WHITE, BLACK = (255, 255, 255), (0, 0, 0)


# 이미지 불러오기 및 크기 조정
def load_and_scale_image(path, size):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size)


logo = load_and_scale_image("logo.png", (screen_width, screen_height))
door_image = load_and_scale_image("door.png", (170, 250))
background1 = load_and_scale_image("background1.png", (screen_width, screen_height))
background2 = load_and_scale_image("background2.png", (screen_width, screen_height))
mob_image = load_and_scale_image("mob.png", (100, 100))
heart_image = load_and_scale_image("heart.png", (30, 30))
attack_image = load_and_scale_image("attack.png", (50, 20))
rule_image = load_and_scale_image("rule.png", (screen_width, screen_height))
rule2_image = load_and_scale_image("rule2.png", (screen_width, screen_height))

# 캐릭터 이미지 설정
characters = ["yujin", "gaeul", "rei", "wonyoung", "liz", "leeseo"]
character_images = {name: load_and_scale_image(f"{name}.png", (100, 150)) for name in characters}

# 기타 변수 설정
clock = pygame.time.Clock()
logo_size, logo_alpha, logo_position = 50, 255, (screen_width // 2, screen_height // 2)
character_selected, character_x, character_y = None, screen_width // 2, screen_height - 180
character_speed_x, jump_count, is_jumping, attack_mode, can_shoot = 7, 10, False, False, True
mob_spawn_timer, mobs, attacks, hearts = 0, [], [], 3
invincibility_timer = 0
INVINCIBILITY_DURATION = 60
current_stage = 1  # 현재 스테이지를 추적하는 변수

# 글꼴 설정
font = pygame.font.Font("DungGeunMo.ttf", 30)


def show_logo():
    global logo_size, logo_alpha
    while logo_alpha > 0:
        screen.fill(WHITE)
        logo_scaled = pygame.transform.scale(logo, (logo_size, logo_size))
        logo_scaled.set_alpha(logo_alpha)
        logo_rect = logo_scaled.get_rect(center=logo_position)
        screen.blit(logo_scaled, logo_rect)
        logo_size += 5
        logo_alpha -= 5
        pygame.display.flip()
        clock.tick(30)


def show_images(images):
    skip_button_rect = pygame.Rect(screen_width - 100, 20, 80, 40)
    skip_text = font.render("Skip", True, BLACK)
    for image in images:
        screen.fill(WHITE)
        screen.blit(image, (0, 0))
        pygame.draw.rect(screen, WHITE, skip_button_rect)
        screen.blit(skip_text, (screen_width - 90, 25))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and skip_button_rect.collidepoint(event.pos):
                return
        pygame.time.delay(1000)


def character_selection():
    global character_selected
    while not character_selected:
        screen.fill(WHITE)
        title_text = font.render("Select a character", True, BLACK)
        screen.blit(title_text, title_text.get_rect(center=(screen_width // 2, 50)))
        start_x = (screen_width - (150 * 3)) // 2
        start_y = (screen_height - (150 * 2)) // 2
        for i, name in enumerate(characters):
            x, y = start_x + (i % 3) * 200, start_y + (i // 3) * 200
            screen.blit(character_images[name], (x, y))
            name_text = font.render(name, True, BLACK)
            screen.blit(name_text, (x + 10, y + 160))
            if pygame.mouse.get_pressed()[0] and pygame.Rect(x, y, 150, 150).collidepoint(pygame.mouse.get_pos()):
                character_selected = name
                return
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


def spawn_mob():
    x, y = screen_width, screen_height - 200
    mobs.append(pygame.Rect(x, y, mob_image.get_width(), mob_image.get_height()))


def check_collision():
    global hearts, invincibility_timer

    if invincibility_timer > 0:
        return False

    character_rect = character_images[character_selected].get_rect(center=(character_x, character_y))
    character_rect.inflate_ip(-50, -50)

    for mob in mobs[:]:
        mob_rect = mob.inflate(-20, -20)
        if character_rect.colliderect(mob_rect):
            hearts -= 1
            invincibility_timer = INVINCIBILITY_DURATION
            mobs.remove(mob)
            if hearts <= 0:
                return True
    return False


def check_door_collision(door_rect):
    character_rect = character_images[character_selected].get_rect(center=(character_x, character_y))
    character_rect.inflate_ip(-50, -50)
    return character_rect.colliderect(door_rect)


def transition_to_next_stage():
    # 전환 이미지 표시
    transition_images = [
        load_and_scale_image(f"image{i}.png", (screen_width, screen_height))
        for i in range(9, 11)  # image9, image10
    ]
    show_images(transition_images)

    # 추가: image10 표시 후 rule2 화면 표시
    show_rule2_screen()

    return 2  # 다음 스테이지 번호 반환


def show_rule_screen():
    waiting = True
    while waiting:
        screen.fill(WHITE)
        screen.blit(rule_image, (0, 0))

        # Start 버튼 추가
        start_button_rect = pygame.Rect(screen_width - 200, screen_height - 100, 150, 50)
        pygame.draw.rect(screen, WHITE, start_button_rect)
        start_text = font.render("Start Game", True, BLACK)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        screen.blit(start_text, start_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                # Start 버튼 클릭 시 게임 시작
                if start_button_rect.collidepoint(event.pos):
                    waiting = False
            elif event.type == KEYDOWN:
                # 스페이스바나 엔터키로도 시작 가능
                if event.key in [K_SPACE, K_RETURN]:
                    waiting = False


def show_rule2_screen():
    waiting = True
    while waiting:
        screen.fill(WHITE)
        screen.blit(rule2_image, (0, 0))

        # Start 버튼 추가
        start_button_rect = pygame.Rect(screen_width - 200, screen_height - 100, 150, 50)
        pygame.draw.rect(screen, WHITE, start_button_rect)
        start_text = font.render("Start Game", True, BLACK)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        screen.blit(start_text, start_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                # Start 버튼 클릭 시 게임 시작
                if start_button_rect.collidepoint(event.pos):
                    waiting = False
            elif event.type == KEYDOWN:
                # 스페이스바나 엔터키로도 시작 가능
                if event.key in [K_SPACE, K_RETURN]:
                    waiting = False


def stage2_game_loop():
    try:
        global character_x, character_y, hearts

        # 보스 이미지 로드 및 위치 설정
        boss_image = load_and_scale_image("boss.png", (250, 300))
        boss_rect = boss_image.get_rect()
        boss_rect.right = screen_width - 50
        boss_rect.centery = screen_height // 1.55
        boss_health = 100

        # 승리 시 표시할 이미지 로드
        magicstick_image = load_and_scale_image("magicstick.png", (100, 200))
        ending_image = load_and_scale_image("ending.png", (screen_width, screen_height))

        # 방향키 이미지 로드
        arrow_images = {
            K_UP: load_and_scale_image("up_arrow.png", (50, 50)),
            K_DOWN: load_and_scale_image("down_arrow.png", (50, 50)),
            K_LEFT: load_and_scale_image("left_arrow.png", (50, 50)),
            K_RIGHT: load_and_scale_image("right_arrow.png", (50, 50))
        }

        # 게임 변수 초기화
        current_sequence = []
        sequence_length = 4
        player_sequence = []
        sequence_timer = 0
        SEQUENCE_DISPLAY_TIME = 30
        game_state = "SHOW_SEQUENCE"

        # 시간 제한 관련 변수
        time_limit = 30 * 30
        current_time = 0

        # 캐릭터 위치 초기화
        character_x = 200
        character_y = screen_height // 1.3

        while True:
            screen.fill(WHITE)
            screen.blit(background2, (0, 0))

            # 캐릭터 그리기
            character_rect = character_images[character_selected].get_rect(center=(character_x, character_y))
            screen.blit(character_images[character_selected], character_rect)

            # 보스 그리기
            screen.blit(boss_image, boss_rect)

            # 보스 체력바 그리기
            health_bar_width = 200
            health_bar_height = 20
            health_bar_x = screen_width - 250
            health_bar_y = 50
            pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
            pygame.draw.rect(screen, (0, 255, 0),
                             (health_bar_x, health_bar_y, health_bar_width * (boss_health / 100), health_bar_height))

            # 하트 표시
            for i in range(hearts):
                screen.blit(heart_image, (10 + i * 40, 10))

            # 남은 시간 표시
            remaining_time = (time_limit - current_time) // 30
            time_text = font.render(f"Time: {remaining_time}s", True, BLACK)
            screen.blit(time_text, (screen_width - 150, 100))

            if game_state == "SHOW_SEQUENCE":
                if not current_sequence:
                    # 새로운 시퀀스 생성
                    current_sequence = [random.choice([K_UP, K_DOWN, K_LEFT, K_RIGHT]) for _ in range(sequence_length)]
                    sequence_timer = 0
                    player_sequence = []

                # 시퀀스 표시
                arrow_spacing = 60
                total_width = len(current_sequence) * arrow_spacing
                start_x = (screen_width - total_width) // 2

                for i, key in enumerate(current_sequence):
                    arrow_rect = arrow_images[key].get_rect(
                        center=(start_x + i * arrow_spacing, screen_height - 100))
                    screen.blit(arrow_images[key], arrow_rect)

                sequence_timer += 1
                if sequence_timer > SEQUENCE_DISPLAY_TIME:
                    game_state = "INPUT"

            elif game_state == "INPUT":
                # 시간 증가
                current_time += 1
                if current_time >= time_limit:
                    hearts -= 1
                    if hearts <= 0:
                        return False
                    game_state = "SHOW_SEQUENCE"
                    current_sequence = []

                # 입력 대기 상태에서도 현재까지의 시퀀스 표시
                arrow_spacing = 60
                total_width = len(current_sequence) * arrow_spacing
                start_x = (screen_width - total_width) // 2

                for i, key in enumerate(current_sequence):
                    if i < len(player_sequence):
                        # 이미 입력된 화살표는 흐리게 표시
                        arrow_surface = arrow_images[key].copy()
                        arrow_surface.set_alpha(128)
                    else:
                        arrow_surface = arrow_images[key]
                    arrow_rect = arrow_surface.get_rect(
                        center=(start_x + i * arrow_spacing, screen_height - 100))
                    screen.blit(arrow_surface, arrow_rect)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN and game_state == "INPUT":
                    if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
                        player_sequence.append(event.key)

                        # 잘못된 입력 체크
                        if player_sequence[-1] != current_sequence[len(player_sequence) - 1]:
                            hearts -= 1
                            if hearts <= 0:
                                return False
                            game_state = "SHOW_SEQUENCE"
                            current_sequence = []

                        # 시퀀스 완성 체크
                        elif len(player_sequence) == len(current_sequence):
                            boss_health -= 20  # 보스 체력 감소
                            if boss_health <= 0:  # 보스를 물리치면 승리
                                # 마법 지팡이 등장 효과
                                stick_alpha = 0
                                stick_rect = magicstick_image.get_rect(center=(screen_width // 2, screen_height // 2))

                                # 페이드인 효과로 마법 지팡이 표시
                                while stick_alpha < 255:
                                    screen.fill(WHITE)
                                    magicstick_surface = magicstick_image.copy()
                                    magicstick_surface.set_alpha(stick_alpha)
                                    screen.blit(magicstick_surface, stick_rect)
                                    pygame.display.flip()
                                    stick_alpha += 5
                                    pygame.time.delay(50)

                                pygame.time.delay(1000)

                                # 엔딩 화면 표시
                                screen.blit(ending_image, (0, 0))
                                pygame.display.flip()
                                pygame.time.delay(3000)
                                return True

                            game_state = "SHOW_SEQUENCE"
                            current_sequence = []

            pygame.display.flip()
            clock.tick(30)
    finally:
        if pygame.mixer.get_init():  # mixer가 초기화되어 있는지 확인
            background_music.stop()

def game_loop():
    try:
        global character_x, character_y, is_jumping, jump_count, attack_mode
        global mob_spawn_timer, hearts, can_shoot, attacks, mobs, invincibility_timer
        global current_stage

        character_facing_right = False
        background_x = 0
        background_move_count = 0

        # 공격 횟수 관련 변수 추가
        remaining_attacks = 5
        fire_image = load_and_scale_image("attack.png", (30, 30))  # 불 이미지 로드

        while True:
            if current_stage == 1:
                screen.fill(WHITE)
                screen.blit(background1, (background_x, 0))
                screen.blit(background1, (background_x + screen_width, 0))

                background_x -= 5
                if background_x <= -screen_width:
                    background_x = 0
                    background_move_count += 1

                if background_move_count >= 4:
                    door_y_position = screen_height // 2 + 117
                    door_rect = door_image.get_rect(center=(screen_width // 2, door_y_position))
                    screen.blit(door_image, door_rect)
                    background_x = 0
                    background_move_count = 4

                    if check_door_collision(door_rect):
                        current_stage = transition_to_next_stage()
                        background_x = 0
                        background_move_count = 0
                        mobs.clear()
                        continue

                if invincibility_timer > 0:
                    invincibility_timer -= 1

                keys = pygame.key.get_pressed()

                if not is_jumping and keys[K_UP]:
                    is_jumping = True
                if is_jumping:
                    character_y -= (jump_count * abs(jump_count)) * 0.4
                    jump_count -= 0.5
                    if jump_count < -10:
                        jump_count = 10
                        is_jumping = False

                # 공격 로직 수정
                if keys[K_DOWN] and can_shoot and remaining_attacks > 0:
                    attacks.append((attack_image.get_rect(center=(screen_width // 2, character_y)),
                                    -10 if character_facing_right else 10))
                    can_shoot = False
                    remaining_attacks -= 1  # 공격 횟수 감소
                if not keys[K_DOWN]:
                    can_shoot = True

                # 남은 공격 횟수 표시 (불 이미지)
                for i in range(remaining_attacks):
                    screen.blit(fire_image, (screen_width - 50 - (i * 40), 20))

                for attack in attacks[:]:
                    attack_rect, direction = attack
                    attack_rect.x += direction
                    screen.blit(attack_image, attack_rect)
                    if attack_rect.x < 0 or attack_rect.x > screen_width:
                        attacks.remove(attack)

                for attack in attacks[:]:
                    attack_rect, _ = attack
                    for mob in mobs[:]:
                        if attack_rect.colliderect(mob):
                            mobs.remove(mob)
                            attacks.remove(attack)
                            break

                if invincibility_timer == 0 or invincibility_timer % 10 >= 5:
                    character_rect = character_images[character_selected].get_rect(
                        center=(screen_width // 2, character_y))
                    character_image = character_images[character_selected] if character_facing_right else \
                        pygame.transform.flip(character_images[character_selected], True, False)
                    screen.blit(character_image, character_rect)

                for i in range(hearts):
                    screen.blit(heart_image, (10 + i * 40, 10))

                if check_collision():
                    background_music.stop()
                    game_over_text = font.render("Game Over", True, BLACK)
                    screen.blit(game_over_text,
                                game_over_text.get_rect(center=(screen_width // 2, screen_height // 2)))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    pygame.quit()
                    sys.exit()

                for mob in mobs[:]:
                    mob.x -= 5
                    if mob.x < 0:
                        mobs.remove(mob)
                    else:
                        screen.blit(mob_image, mob)

                mob_spawn_timer += 1
                if mob_spawn_timer >= random.randint(50, 200):
                    spawn_mob()
                    mob_spawn_timer = 0

            elif current_stage == 2:
                # 스테이지 2 실행
                game_result = stage2_game_loop()
                if game_result:
                    # 게임 클리어
                    victory_text = font.render("Game Clear!", True, BLACK)
                    screen.blit(victory_text, victory_text.get_rect(center=(screen_width // 2, screen_height // 2)))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    pygame.quit()
                    sys.exit()
                else:
                    # 게임 오버
                    game_over_text = font.render("Game Over", True, BLACK)
                    screen.blit(game_over_text, game_over_text.get_rect(center=(screen_width // 2, screen_height // 2)))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
    finally:
        background_music.stop()
        pygame.quit()
        sys.exit()


# 메인 게임 실행
show_logo()
show_images([load_and_scale_image(f"image{i}.png", (screen_width, screen_height)) for i in range(1, 9)])
character_selection()
show_rule_screen()  # 캐릭터 선택 후 규칙 화면 표시
game_loop()