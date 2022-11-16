include "globals.mzn";
include "diffn.mzn";

int: field_w = 10;
int: field_h = 20;
int: n;
array[1..field_h, 1..field_w] of var 0..1: field;

set of int: blocks = 1..n;

array[blocks] of int: blocks_x;
array[blocks] of int: blocks_y;
array[blocks] of int: blocks_w;
array[blocks] of int: blocks_h;

array[1..field_w] of int: pos_y_full;


array[1..2] of int: widths;
array[1..2] of int: heights;

array[1..2] of var bool: rotations;
array[1..2] of var int: actual_widths = [(widths[i]*(1-rotations[i]) + (heights[i])*rotations[i]) | i in 1..2];
array[1..2] of var int: actual_heights = [(widths[i]*rotations[i]) + (heights[i]*(1-rotations[i])) | i in 1..2];

var 0..field_h: full_rows;

array[1..2] of var 0..field_w-min(widths): pos_x;
array[1..2] of var min(pos_y_full)..max(pos_y_full): pos_y;

constraint pos_y[1] = pos_y_full[pos_x[1] + 1];
constraint pos_y[2] = pos_y_full[pos_x[2] + 1];

constraint max(i in 1..2)(pos_x[i] + actual_widths[i]) <= field_w;
constraint max(i in 1..2)(pos_y[i] + actual_heights[i]) <= field_h;
constraint diffn(blocks_x ++ pos_x, blocks_y ++ pos_y, blocks_w ++ actual_widths, blocks_h ++ actual_heights);
%constraint cumulative(blocks_x ++ pos_x, blocks_w ++ actual_widths, blocks_h ++ actual_heights, field_h);
%constraint cumulative(blocks_y ++ pos_y, blocks_h ++ actual_heights, blocks_w ++ actual_widths, field_w);

%constraint forall(
%    block in blocks,
%    i in blocks_x[block]..blocks_x[block]+blocks_w[block]-1,
%    j in blocks_y[block]..blocks_y[block]+blocks_h[block]-1
%)(
%    field[j+1, i+1] = 1
%);

constraint forall(block in 1..2, i in 0..field_w-1, j in 0..field_h-1)(
    if(i in pos_x[block]..pos_x[block]+actual_widths[block] - 1 /\
       j in pos_y[block]..pos_y[block]+actual_heights[block] - 1) 
       then field[j+1,i+1] = 1 
       else field[j+1,i+1] = 0 
       endif
);

%constraint forall(
%    block in 1..2,
%    i in pos_x[block]..pos_x[block]+actual_widths[block] - 1,
%    j in pos_y[block]..pos_y[block]+actual_heights[block] - 1 
%)(
%    field[j+1,i+1] = 1
%);

constraint full_rows = sum([count(field[i,..], 1) div 10 == 1| i in 1..field_h]);

solve :: seq_search([
    int_search(pos_x, first_fail, indomain_min),
    int_search(rotations, first_fail, indomain_min),
    int_search(field, first_fail, indomain_min),
    int_search([full_rows], smallest, indomain_min)])    
    maximize full_rows;
    
output [
    "full rows = ", show(full_rows), "\n",
    "pos_x = ", show(pos_x), "\n",
    "widths = ", show(actual_widths), "\n", 
    "heights = ", show(actual_heights), "\n",
    "rotations = ", show(rotations), "\n",
    "field = ", "\n",
    show(field[20,..]), "\n",
    show(field[19,..]), "\n",
    show(field[18,..]),"\n",
    show(field[17,..]),"\n",
    show(field[16,..]),"\n",
    show(field[15,..]),"\n",
    show(field[14,..]),"\n",
    show(field[13,..]),"\n",
    show(field[12,..]),"\n",
    show(field[11,..]),"\n",
    show(field[10,..]),"\n",
    show(field[9,..]),"\n",
    show(field[8,..]),"\n",
    show(field[7,..]),"\n",
    show(field[6,..]),"\n",
    show(field[5,..]),"\n",
    show(field[4,..]),"\n",
    show(field[3,..]),"\n",
    show(field[2,..]),"\n",
    show(field[1,..]),"\n"
]




