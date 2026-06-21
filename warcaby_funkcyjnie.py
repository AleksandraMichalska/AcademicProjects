from time import sleep
import sys
import numpy as np
import copy

# Paradygmat funkcyjny został zastosowany do algorytmu minimax z dodatkiem alfa-beta,
# czyli do podejmowania decyzji o następnym ruchu przez komputer.
# Z części funkcji korzysta też gracz np. generowanie wszystkich możliwych ruchów.
# Dla oszczędności pamięci, funkcje sterujące rozgrywką, na przykład cykl kolejek,
# są zrealizowane niefunkcyjnie. 
# Uproszczony ruch damki: porusza się tylko raz w jedną przekątną
# Konstrukcja możliwego ruchu: (start_row, start_column, end_row, end_column, end_chart, captured)

# K kom, G - gracz
chart = [["","K", "", "K", "", "K", "", "K"],
         ["K","", "K", "", "K", "", "K", ""],
         ["","K", "", "K", "", "K", "", "K"],
         ["","", "", "", "", "", "", ""],
         ["","", "", "", "", "", "", ""],
         ["G","", "G", "", "G", "", "G", ""],
         ["","G", "", "G", "", "G", "", "G"],
         ["G","", "G", "", "G", "", "G", ""]
         ]

#obsługa ruchu komputera
def npc_turn(chart):
    print("Kolej komputera")
    sleep(2)
    best_decision = ab(chart, "K", "K", 3, -np.inf, np.inf)
    return best_decision[1]

#obsługa wyboru ruchu gracza
def player_turn(chart):
    print("Twoja kolej")
    print("Możliwe ruchy: ")
    moves = filtered_possible_moves(chart, "G")
    for m in range(len(moves)):
        print(f"{m}. ({moves[m][0]}, {moves[m][1]})-> ({moves[m][2]}, {moves[m][3]})")
    moves_numbers_str = string_numbers(0, len(moves), [])
    while True:
        players_choice = input("Wybierz ruch: ")
        if players_choice == "q":
            sys.exit(0)
        elif players_choice not in moves_numbers_str:
            print("Złe wejście. Spróbuj ponownie")
        else:
            return moves[int(players_choice)][4] # zwróć planszę po tym ruchu
        
def print_chart(chart):
    print(" 0   1   2   3   4   5   6   7")
    print_rows(chart, 0)
    print("--------------------------------")

def print_rows(chart, row_index):
    if row_index > 7:
        return 0
    row = chart[row_index]
    print("--------------------------------")
    print("|", end='')
    print_columns(row, 0)
    print(" "+str(row_index))
    if row_index < 7:
        print_rows(chart, row_index+1)
    return 0

def print_columns(row, column_index):
        if column_index > 7:
            return 0
        column = row[column_index]
        if len(column) == 2:
            print(column, end='')
        elif(column == ""):
            print("  ", end='')
        else:
            print(" " + column, end='')
        print("| ", end='')
        return print_columns(row, column_index+1)


def string_numbers(number, end, list):
    if(number > end):
        return list
    else:
        str_number = [str(number)]
        return string_numbers(number+1, end, list+str_number)
    
def filtered_possible_moves(chart, my_pawn):
    possible_moves_list = possible_moves(chart, 0, 0, my_pawn, [], False)
    possible_moves_captured = loop_possible_moves_captured(possible_moves_list, [], 0)
    max_captured = operator_questionmark((len(possible_moves_captured) != 0), max(possible_moves_captured), 0)
    filtered_possible_moves_list = loop_filter_moves(possible_moves_list, [], 0, max_captured)
    return filtered_possible_moves_list

def loop_possible_moves_captured(input_list, output_list, index):
    if index == len(input_list):
        return output_list
    else:
        element = [input_list[index][5]]
        return loop_possible_moves_captured(input_list, output_list+element, index+1)

def operator_questionmark(condition, iftrue, iffalse):
    if(condition):
        return iftrue
    else:
        return iffalse
    
def loop_filter_moves(input_list, output_list, index, max_captured):
    if index == len(input_list):
        return output_list
    else:
        if(input_list[index][5] == max_captured):
            element = [input_list[index]]
            return loop_filter_moves(input_list, output_list+element, index+1, max_captured)
        else:
            return loop_filter_moves(input_list, output_list, index+1, max_captured)

# Zwraca listę krotek. Każda krotka to możliwy ruch.
def possible_moves(chart, row, column, my_pawn, current_possibles, is_jumping):
    checked_row = row
    checked_column = column
    if(column > 7):
        if(row == 7):
            return current_possibles
        else:
            checked_row = row+1
            checked_column = 0 
    if(chart[checked_row][checked_column] == my_pawn): # jeśli nasz pionek tu jest
        adjacent = adjacent_f(checked_row, checked_column)
        new_possible_jump_moves = loop_possible_jump_moves(chart, adjacent, 0, my_pawn, checked_row, checked_column, [])        
        if len(new_possible_jump_moves) == 0:
            if(not is_jumping): # nie bijemy i dotychczas nie było bicia. Możemy wygenerować te ruchy
                new_plain_moves = loop_plain_moves(chart, adjacent, 0, checked_row, checked_column, my_pawn, [])
                return possible_moves(chart, checked_row, checked_column+1, my_pawn, current_possibles+new_plain_moves, is_jumping)
            return possible_moves(chart, checked_row, checked_column+1, my_pawn, new_possible_jump_moves+current_possibles, is_jumping)
        else: # Wygenerowano nowe skoki. Podajemy teraz is_jumping jako True
            return possible_moves(chart, checked_row, checked_column+1, my_pawn, new_possible_jump_moves+current_possibles, True)
    elif chart[checked_row][checked_column] == "D"+my_pawn:
        new_D_moves = possible_D_moves(chart, checked_row, checked_column, my_pawn) 
        return possible_moves(chart, checked_row, checked_column+1,my_pawn, current_possibles+new_D_moves, is_jumping)
    else: # pionek na tym polu nie jest mój
        return possible_moves(chart, checked_row, checked_column+1, my_pawn, current_possibles, is_jumping)

def loop_possible_jump_moves(chart, adjacent, index_adjacent, my_pawn, checked_row, checked_column, new_possibles):
    if index_adjacent == len(adjacent):
        return new_possibles
    field = adjacent[index_adjacent]
    if(chart[field[0]][field[1]] not in [my_pawn, "D"+my_pawn, ""]):
        field_behind = get_field_behind(checked_row, checked_column, field[0], field[1])
        if(field_behind != (-1, -1)):
            if(chart[field_behind[0]][field_behind[1]] == ""):
                generated_jumps = jumping_moves(checked_row, checked_column, field_behind[0], field_behind[1], field[0], field[1], chart, 0, my_pawn)
                jumps_converted_to_moves = jumps_to_moves(generated_jumps, 0, checked_row, checked_column, [])
                return loop_possible_jump_moves(chart, adjacent, index_adjacent+1, my_pawn, checked_row, checked_column, new_possibles+jumps_converted_to_moves)
    return loop_possible_jump_moves(chart, adjacent, index_adjacent+1, my_pawn, checked_row, checked_column, new_possibles)

def jumps_to_moves(generated_jumps, jump_index, checked_row, checked_column, moves):
    if jump_index == len(generated_jumps):
        return moves
    jump = generated_jumps[jump_index]
    new_jump_move = [(checked_row, checked_column, jump[0], jump[1], jump[2], jump[3])]
    return jumps_to_moves(generated_jumps, jump_index+1, checked_row, checked_column, moves+new_jump_move)

def loop_plain_moves(chart, adjacent, adjacent_index, checked_row, checked_column, my_pawn, new_possibles):
    if adjacent_index == len(adjacent):
        return new_possibles
    field = adjacent[adjacent_index]
    if(chart[field[0]][field[1]] == ''):
        if(direction_ok(checked_row, field[0], my_pawn)):
            chart_simulation = update_chart_plain(chart, field, checked_row, checked_column, my_pawn)
            new_move = [(checked_row, checked_column, field[0], field[1], chart_simulation, 0)]
            return loop_plain_moves(chart, adjacent, adjacent_index+1, checked_row, checked_column, my_pawn, new_possibles+new_move)
    return loop_plain_moves(chart, adjacent, adjacent_index+1, checked_row, checked_column, my_pawn, new_possibles)

def possible_D_moves(chart, start_row, start_column, my_pawn):
    moves_L_U = moves_diagonally_with_preprocess(chart, start_row, start_column, my_pawn,-1,-1)
    moves_L_D = moves_diagonally_with_preprocess(chart, start_row, start_column, my_pawn,1,-1)
    moves_R_U = moves_diagonally_with_preprocess(chart, start_row, start_column, my_pawn,-1,1)
    moves_R_D = moves_diagonally_with_preprocess(chart, start_row, start_column, my_pawn,1,1)
    return moves_L_D+moves_R_D+moves_L_U+moves_R_U

def moves_diagonally_with_preprocess(chart, start_row, start_column, my_pawn, step_r, step_c):
    diagonal = diagonal_map(chart, start_row, start_column, [], step_r, step_c)
    # przytnij listę do pierwszego mojego pionka. Nie można przeskoczyć swoich pionków
    first_occurence_pawn = find_pawn(my_pawn, diagonal)
    first_occurence_D = find_pawn("D"+my_pawn, diagonal)
    decreased_1 = decrease_1(first_occurence_pawn, first_occurence_D, diagonal) 
    # przytnij listę do ostatniego pustego pola
    decreased_2 = decrease_2(decreased_1, len(decreased_1)-1)
    captured = len(decreased_2) - decreased_2.count("")
    return moves_diagonally(chart, decreased_2, my_pawn, start_row, start_column, [], len(decreased_2)-1, step_r, step_c, captured) 

def diagonal_map(chart, checked_row, checked_column, map, step_r, step_c):
    r = checked_row + step_r
    c = checked_column + step_c
    if(r < 0 or c < 0 or r > 7 or c > 7):
        return map
    field = [chart[r][c]] # pionek na tym polu lub ""
    return diagonal_map(chart, r, c, map+field, step_r, step_c)

def decrease_1(first_occurence_pawn, first_occurence_D, diagonal):
    if(first_occurence_pawn == -1 and first_occurence_D > -1):
        return diagonal[0:first_occurence_D]
    elif(first_occurence_pawn > 0 and first_occurence_D == -1):
        return diagonal[0:first_occurence_pawn]
    elif(first_occurence_D == -1 and first_occurence_pawn == -1):
        return diagonal
    else: # oba pionki są obecne na liście
        return diagonal[0:min(first_occurence_pawn, first_occurence_D)]

def decrease_2(diagonal, index):
    if(index < 0):
        return diagonal
    if diagonal[index] == "":
        return diagonal
    return decrease_2(diagonal[0:-1], index-1)

def find_pawn(pawn, list):
    if(list.count(pawn) > 0):
        return list.index(pawn)
    else:
        return -1

def moves_diagonally(chart, map, my_pawn, start_row, start_column, current_moves, index, r_multiplier, c_multiplier, captured):
    if index < 0:
        return current_moves
    elif(map[index] == ""):
        end_row = r_multiplier*(index+1)+start_row
        end_column = c_multiplier*(index+1)+start_column
        simulation_chart = update_chart_D(chart, start_row, start_column, end_row, end_column, index, r_multiplier, c_multiplier, my_pawn)
        new_move = [(start_row, start_column, end_row, end_column, simulation_chart, captured)]
        return moves_diagonally(chart, map, my_pawn,start_row, start_column, current_moves+new_move, index-1, r_multiplier, c_multiplier, captured)
    return current_moves

def adjacent_f(checked_row, checked_column):
    if(checked_row == 0 and checked_column == 0):
        return [(1,1)]
    elif(checked_row == 0 and checked_column == 7):
        return [(1,6)]
    elif(checked_row == 7 and checked_column == 7):
        return [(6,6)]
    elif(checked_row == 7 and checked_column == 0):
        return [(6,1)]
    elif(checked_row == 7):
        return [(6,checked_column-1), (6,checked_column+1)]
    elif(checked_row == 0):
        return [(1,checked_column-1), (1,checked_column+1)]
    elif(checked_column == 7):
        return [(checked_row-1,6), (checked_row+1, 6)]
    elif(checked_column == 0):
        return [(checked_row-1,1), (checked_row+1, 1)]
    else:
        return [(checked_row-1, checked_column-1), (checked_row-1, checked_column+1), (checked_row+1, checked_column-1), (checked_row+1, checked_column+1)]

def jumping_moves(start_row, start_column, end_row, end_column, enemy_row, enemy_column, chart, captured, my_pawn):
    new_chart = update_chart_jump(chart, (start_row, start_column), (enemy_row, enemy_column), (end_row, end_column), my_pawn)
    adjacent = adjacent_f(end_row, end_column)
    free_field_enemy_field = loop_free_field_enemy_field(new_chart, adjacent, 0, my_pawn, end_row, end_column, [])
    if(len(free_field_enemy_field) == 0): # z pola startowego wywodzi się jeden skok
        generated_jump = [(end_row, end_column, new_chart, captured+1)]
        return generated_jump
    else: # z pola startowego wywodzi się kilka różnych skoków
        new_generated_jumps = loop_generate_multiple_jumps(new_chart, captured, my_pawn, 0, free_field_enemy_field, end_row, end_column, [])
        return new_generated_jumps   

def loop_free_field_enemy_field(new_chart, adjacent, adjacent_index, my_pawn, end_row, end_column, pairs):
    if adjacent_index == len(adjacent):
        return pairs
    field = adjacent[adjacent_index]
    if(new_chart[field[0]][field[1]] not in [my_pawn,"D"+my_pawn, ""]):
        field_behind = get_field_behind(end_row, end_column, field[0], field[1])
        if(field_behind != (-1, -1)):
            if(new_chart[field_behind[0]][field_behind[1]] == ""):
                new_pair = [[field_behind, field]]
                return loop_free_field_enemy_field(new_chart, adjacent, adjacent_index+1, my_pawn, end_row, end_column, pairs+new_pair)
    return loop_free_field_enemy_field(new_chart, adjacent, adjacent_index+1, my_pawn, end_row, end_column, pairs)

def loop_generate_multiple_jumps(new_chart, captured, my_pawn, field_index, free_field_enemy_field, end_row, end_column, generated_jumps):
    if field_index == len(free_field_enemy_field):
        return generated_jumps
    pair = free_field_enemy_field[field_index]
    new_generated_jumps = jumping_moves(end_row, end_column, pair[0][0], pair[0][1], pair[1][0], pair[1][1], new_chart, captured+1, my_pawn)
    return loop_generate_multiple_jumps(new_chart, captured, my_pawn, field_index+1, free_field_enemy_field, end_row, end_column, generated_jumps+new_generated_jumps)


def get_field_behind(my_row, my_column, enemy_row, enemy_column):
    if(my_row > enemy_row and my_column > enemy_column):
        if(enemy_row-1 < 0 or enemy_column-1 < 0):
            return (-1, -1)
        else:
            return (enemy_row-1, enemy_column-1)
    elif(my_row > enemy_row and my_column < enemy_column):
        if(enemy_row-1 < 0 or enemy_column+1 > 7):
            return (-1, -1)
        else:
            return (enemy_row-1, enemy_column+1) 
    elif(my_row < enemy_row and my_column > enemy_column):
        if(enemy_row+1 > 7 or enemy_column-1 < 0):
            return (-1, -1)
        else:
            return (enemy_row+1, enemy_column-1)
    else: #(my_row < enemy_row and my_column < enemy_column):
        if(enemy_row+1 > 7 or enemy_column+1 > 7):
            return (-1, -1)
        else:
            return (enemy_row+1, enemy_column+1)
        
def direction_ok(my_row, end_row, my_pawn):
    if(my_pawn == "K"):
        return not (my_row > end_row) # jeśli próbuję przejść do wyższego rzędu, zwróć False
    else: # my_pawn = "G"
        return not (my_row < end_row) # jeśli próbuję przejść do niższego rzędu, zwróć False

def winner(chart):
    com_count, player_count = count_pawns(chart, 0, 0, 0)
    if(com_count == 0):
        return "G"
    elif(player_count == 0):
        return "K"
    else:
        return "N"
    
def count_pawns(chart, row_index, com_count, player_count):
    if row_index == len(chart):
        return com_count, player_count
    row = chart[row_index]
    com_part = row.count("K") + row.count("DK")
    player_part = row.count("G") + row.count("DG")
    return count_pawns(chart, row_index+1, com_count+com_part, player_count+player_part)

def ab(chart, my_symbol, symbol, depth, a, b):
    if (winner(chart) in ["K", "G"]) or (depth == 0):
        return state_assesment(chart, my_symbol), chart
    successor_moves = filtered_possible_moves(chart, symbol)
    successors_charts = extract_charts([], 0, successor_moves)
    chosen_move = main_loop_ab(successors_charts, 0, depth, my_symbol, symbol, [], a, b)
    if my_symbol == symbol:
        return a, chosen_move
    else:
        return b, chosen_move
    
def main_loop_ab(successors_charts, successor_index, depth, my_symbol, symbol, chosen_move, a, b):
    if successor_index == len(successors_charts):
        return chosen_move
    successor = successors_charts[successor_index]
    next_symbol = get_next_symbol(symbol)
    decision = ab(successor, my_symbol, next_symbol, depth-1, a, b)
    if my_symbol == symbol:
        # nasza kolej, wybieramy najlepsze rozwiązanie. Nadpisujemy tylko a
        if decision[0] > a:
            return main_loop_ab(successors_charts, successor_index+1, depth, my_symbol, symbol, successor, decision[0], b)
    else:
        #kolej przeciwnika, wybieramy najgorsze rozwiązanie. Nadpisujemy tylko b
        if decision[0] < b:
            return main_loop_ab(successors_charts, successor_index+1, depth, my_symbol, symbol, successor, a, decision[0])
    return main_loop_ab(successors_charts, successor_index+1, depth, my_symbol, symbol, successor, a, b)

def get_next_symbol(current_symbol):
    if current_symbol == "K":
        return "G"
    return "K"

def extract_charts(charts, index, moves):
    if index == len(moves):
        return charts
    chart = [moves[index][4]]
    return extract_charts(charts+chart, index+1, moves)

#obliczanie wartości liczbowej planszy z perspektywy gracza o danym symbolu
def state_assesment(chart, symbol):
    who_wins = winner(chart)
    if who_wins == symbol:
        return 100 # wygrana
    elif who_wins:
        return -100 # przegrana
    # heurystyka
    if(symbol == "K"):
        return points_for_row(0, chart, 0, 1, -1)
    else:
        return points_for_row(0, chart, 0, -1, 1)

def points_for_row(result, chart, row_index, mul1, mul2):
    if row_index == len(chart):
        return result
    row = chart[row_index]
    number_to_add  = mul1*row.count("K") + mul1*2*row.count("DK") + mul2*row.count("G") + mul2*row.count("DG")
    return points_for_row(result+number_to_add, chart, row_index+1, mul1, mul2)


def is_d(my_pawn, arrived_row):
    return ((my_pawn == "K" and arrived_row==7) or (my_pawn=="G" and arrived_row==0))

def update_chart_jump(chart, start, enemy, end, pawn):
    def updated_row(row_index):
        row = chart[row_index]
        return [
            "" if (row_index, column_index) in [start, enemy] else
            "D"+pawn if (row_index, column_index) == end and is_d(pawn, end[0]) else
            pawn if (row_index, column_index) == end else
            field
            for column_index, field in enumerate(row)
        ]
    
    return [updated_row(row_index) for row_index in range(len(chart))]

def update_chart_D(chart, start_row, start_column, end_row, end_column, index, r_multiplier, c_multiplier, my_pawn):
    def updated_row(row_index):
        row = chart[row_index]
        return [
            "" if (row_index, column_index) in intermediate_fields
            else "D" + my_pawn if (row_index, column_index) == (end_row, end_column)
            else field
            for column_index, field in enumerate(row)
        ]
    intermediate_fields = [
        (start_row + i * r_multiplier, start_column + i * c_multiplier)
        for i in range(index + 1)
    ]
    return [updated_row(row_idx) for row_idx in range(len(chart))]

def update_chart_plain(chart, field, checked_row, checked_column, my_pawn):
    def updated_row(row_index):
        row = chart[row_index]
        return [
            "" if (row_index, column_index) == (checked_row, checked_column)
            else ("D" + my_pawn if is_d(my_pawn, row_index) else my_pawn)
                if (row_index, column_index) == field
            else field_value
            for column_index, field_value in enumerate(row)
        ]
    return [updated_row(row_index) for row_index in range(len(chart))]


if __name__ == "__main__":
    print("Warcaby")
    player_starts_bool = False
    while True:
        player_starts = input("Czy chcesz zacząć? t/n:")
        if player_starts == "q":
            sys.exit(0)
        elif player_starts == "t":
            print_chart(chart)
            player_starts_bool = True
            new_chart = player_turn(chart)
            chart = copy.deepcopy(new_chart)
            print_chart(chart)
            break
        elif player_starts == "n":
            break
        else:
            print("Złe wejście. Spróbuj ponownie.")
    if(not player_starts_bool):
        print_chart(chart)
    while True:
        new_chart = npc_turn(chart)
        chart = copy.deepcopy(new_chart)
        print_chart(chart)
        win = winner(chart)
        if(win != "N"):
            break
        new_chart = player_turn(chart)
        chart = copy.deepcopy(new_chart)
        print_chart(chart)
        win = winner(chart)
        if(win != "N"):
            break
    if(win == "K"):
        print("Komputer wygrywa")
    else:
        print("Wygrywasz")