import cv2 as cv
import numpy as np
import math
from sys import argv

# usage of opencv credits to Shanmukha Ranganath

# Read the input image and save the original
original = cv.imread(argv[1])
# cv.imwrite("solution/original.png", original)

# Convert the image to grayscale
gray = cv.cvtColor(original, cv.COLOR_BGR2GRAY)

# Find contours in the grayscale image and sort them by area
contours, _ = cv.findContours(gray, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
contours = sorted(contours, key=cv.contourArea, reverse=True)

# Extract the bounding box of the puzzle grid (using the second largest contour)
x, y, w, h = cv.boundingRect(contours[1])

# Crop the grid area from the original image
grid = original[y:y+h, x:x+w]
# cv.imwrite("solution/grid.png", grid)

# Convert the cropped grid to grayscale
gray = cv.cvtColor(grid, cv.COLOR_BGR2GRAY)
# cv.imwrite("solution/gray-grid.png", gray)

# Find contours again in the cropped grayscale grid
contours, _ = cv.findContours(gray, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
contours = sorted(contours, key=cv.contourArea)

# Determine the total number of cells in the grid
total_cells = len(contours) - 2
grid_size = int(math.sqrt(total_cells))

# Check if the detected cells form a complete square grid
if total_cells != grid_size**2:
    print("Unable to detect full grid! Aborting")

# Calculate individual cell dimensions
cell_width = w // grid_size
cell_height = h // grid_size

# Initialize color mappings and board representation
colors = []
board = []
color_index = 1
color_map = {}
reverse_color_map = {}
padding = 10

# Iterate through each cell in the grid
for i in range(grid_size):
    row = []
    for j in range(grid_size):
        # Calculate cell coordinates with padding
        cell_x = j * cell_width
        cell_y = i * cell_height
        padding = 15
        cell = grid[cell_y+padding:cell_y+cell_height-padding, cell_x+padding:cell_x+cell_width-padding]

        # Get the average color of the cell
        avg_color = cell.mean(axis=0).mean(axis=0)
        avg_color = avg_color.astype(int)
        avg_color = tuple(avg_color)

        # Map the color to a unique index if not already mapped
        if avg_color not in color_map:
            color_map[avg_color] = str(color_index)
            reverse_color_map[str(color_index)] = avg_color
            color_index += 1

        # Add the color index to the row
        row.append(color_map[avg_color])

    # Add the row to the board
    board.append(row)

placed_pieces = set()
color_used = set()
column_used = set()

def solver(l, c, r):
    if r == 0:
        return True
    if possible_play(l, c):
        placed_pieces.add((l, c))
        color_used.add(board[l][c])
        column_used.add(c)
        # print_board()
        for i in range(len(board)):
            if solver(l+1, i, r-1):
                return True
        placed_pieces.remove((l, c))
        color_used.remove(board[l][c])
        column_used.remove(c)
    return False

def possible_play(l, c):
    if board[l][c] in color_used:
        return False
    if c in column_used:
        return False
    if (l-1, c-1) in placed_pieces or (l-1, c+1) in placed_pieces:
        return False
    return True

def print_board():
    for i in range(len(board)):
        for j in range(len(board)):
            if (i, j) in placed_pieces:
                print("Q", end="")
            else:
                print(".", end="")
        print()
    print()

for i in range(len(board)):
    if solver(0, i, len(board)):
        break
# print("Solution:")
# print_board()
# print(placed_pieces)

# Initialize an empty output image to recreate the grid
output_image = np.ones((h, w, 3), dtype="uint8")

# Set border and letter sizes for visual elements
border_size = 1
letter_height = 10

# Iterate through each cell of the grid
for i in range(grid_size):
    for j in range(grid_size):
        # Calculate the position of the current cell
        cell_x = j * cell_width
        cell_y = i * cell_height

        # Retrieve the color for the current cell from the reverse color map
        color_pick = reverse_color_map.get(board[i][j])
        color = (int(color_pick[0]), int(color_pick[1]), int(color_pick[2]))

        # Draw the cell with the appropriate color
        output_image = cv.rectangle(
            output_image,
            (cell_x + border_size, cell_y + border_size),
            (cell_x + cell_width - border_size, cell_y + cell_height - border_size),
            color,
            thickness=-1
        )

        # Draw grid lines between the cells
        output_image = cv.line(
            output_image,
            (cell_x, cell_y),
            (cell_x + cell_width, cell_y),
            (0, 0, 0),
            thickness=1
        )

        # If a queen is placed in this cell, place the crown image at the center of the cell
        if (i, j) in placed_pieces:
            # Load the crown image
            crown = cv.imread("utils/golden_crown.png", cv.IMREAD_UNCHANGED)
            
            # Resize crown to fit within the cell (e.g., 70% of cell size)
            crown_size = int(min(cell_width, cell_height) * 0.7)
            crown = cv.resize(crown, (crown_size, crown_size))
            
            # Calculate position to center the crown in the cell
            crown_x = cell_x + (cell_width - crown_size) // 2
            crown_y = cell_y + (cell_height - crown_size) // 2
            
            # Overlay the crown image
            if crown.shape[2] == 4:  # If crown has alpha channel
                alpha = crown[:, :, 3] / 255.0
                for c in range(3):
                    output_image[crown_y:crown_y+crown_size, crown_x:crown_x+crown_size, c] = \
                    alpha * crown[:, :, c] + (1 - alpha) * output_image[crown_y:crown_y+crown_size, crown_x:crown_x+crown_size, c]
            else:  # No alpha channel
                output_image[crown_y:crown_y+crown_size, crown_x:crown_x+crown_size] = crown

# Save the output image with the solved board displayed
cv.imwrite("static/solution.png", output_image)