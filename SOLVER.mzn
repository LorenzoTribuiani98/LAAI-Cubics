include "globals.mzn";
include "diffn.mzn";
include "function.mzn";

int: field_w = 10;
int: field_h = 20;
int: n;
array[1..field_h, 1..field_w] of var 0..1: field;


set of int: blocks = 1..n;
set of int: new_blocks = 1..2;
array[blocks] of int: blocks_x;
array[blocks] of int: blocks_y;
array[blocks] of int: blocks_w;
array[blocks] of int: blocks_h;

array[1..field_w] of var int: pos_y_full;

array[new_blocks] of int: widths;
array[new_blocks] of int: heights;

array[new_blocks] of var bool: rotations;
array[new_blocks] of var int: actual_widths = [(widths[i]*(1-rotations[i]) + heights[i]*rotations[i]) | i in new_blocks];
array[new_blocks] of var int: actual_heights = [(widths[i]*rotations[i]) + heights[i]*(1-rotations[i])| i in new_blocks];

var 0..field_h: full_rows;
var 0..field_w: longest_row;
var 1..field_h: h;

array[new_blocks] of var 0..field_w-1: pos_x;
array[new_blocks] of var 0..field_h-1: pos_y;

constraint max(i in new_blocks)(pos_x[i] + actual_widths[i]) <= field_w;
constraint max(i in new_blocks)(pos_y[i] + actual_heights[i]) <= h;
constraint diffn(blocks_x++pos_x, blocks_y++pos_y, blocks_w++actual_widths, blocks_h++actual_heights);
constraint cumulative(blocks_x++pos_x, blocks_w++actual_widths, blocks_h++actual_heights, h);
constraint cumulative(blocks_y++pos_y, blocks_h++actual_heights, blocks_w++actual_widths, field_w);


constraint forall(
              i in 0..field_w-1,
              j in 0..field_h-1)(
    exists(block in blocks)(
        ((i in blocks_x[block]..blocks_x[block]+blocks_w[block]-1 
        /\j in blocks_y[block]..blocks_y[block]+blocks_h[block]-1))) 
        \/
    exists(block in new_blocks)(
        (i in pos_x[block]..pos_x[block]+actual_widths[block] - 1 
        /\j in pos_y[block]..pos_y[block]+actual_heights[block] - 1))
        <-> (field[j+1, i+1] = 1)
);

constraint pos_y_full = [find_pos_y(field[..,i], 1)| i in 1..field_w];

constraint forall(i in new_blocks)(pos_y[i] = pos_y_full[pos_x[i] + 1] - actual_heights[i]);

constraint forall(i in new_blocks)(field[pos_y[i],pos_x[i]+1] = 1 \/ pos_y[i] = 0);

constraint let {array[1..field_h] of var int: lenghts = [count(field[j,..],1) | j in 1..field_h]} in longest_row = max(i in 1..field_h)(lenghts[i]);

constraint full_rows = sum([count(field[i,..], 1) div 10 == 1| i in 1..field_h]);

solve :: seq_search([
    int_search(pos_x, first_fail, indomain_min),
    int_search(rotations, first_fail, indomain_min)])    
    maximize (longest_row +full_rows + (field_h - h));
    
output [
    "full_rows = ", show(full_rows), "\n",
    "longest_row = ", show(longest_row), "\n", 
    "height = ", show(h), "\n",
    "maximizing index = ", show(longest_row +full_rows + (field_h - h)), "\n",
    "pos_x = ", show(pos_x), "\n",
    "pos_y = ", show(pos_y), "\n",
    "pos_y_full = ", show(pos_y_full), "\n",
    "rotations = ", show(rotations), "\n",
    "actual_w = ", show(actual_widths), "\n",
    "actual_h = ", show(actual_heights), "\n",
    "field = " ,
    show(field[20,..]), "\n",
    show(field[19,..]), "\n",
    show(field[18,..]), "\n",
    show(field[17,..]), "\n",
    show(field[16,..]), "\n",
    show(field[15,..]), "\n",
    show(field[14,..]), "\n",
    show(field[13,..]), "\n",
    show(field[12,..]), "\n",
    show(field[11,..]), "\n",
    show(field[10,..]), "\n",
    show(field[9,..]), "\n",
    show(field[8,..]), "\n",
    show(field[7,..]), "\n",
    show(field[6,..]), "\n",
    show(field[5,..]), "\n",
    show(field[4,..]), "\n",
    show(field[3,..]), "\n",
    show(field[2,..]), "\n",
    show(field[1,..]), "\n",
]




