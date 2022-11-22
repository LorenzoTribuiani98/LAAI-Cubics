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
var 0..field_w*field_h: unreachable;
var 1..field_h: h;

array[new_blocks] of var 0..field_w-1: pos_x;
array[new_blocks] of var 0..field_h-1: pos_y;

array[1..3] of int: priorities = [10,5,10];

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

constraint pos_y_full = [find_last(field[..,i], 1)| i in 1..field_w];

constraint forall(i in new_blocks)(pos_y[i] = pos_y_full[pos_x[i] + 1] - actual_heights[i]);

constraint (pos_x[2] in pos_x[1]..pos_x[1]+widths[1] \/
            pos_x[2]+widths[2] in pos_x[1]..pos_x[1]+widths[1]) ->
            pos_y[1] < pos_y[2];

constraint forall(i in new_blocks)(field[pos_y[i],pos_x[i]+1] = 1 \/ pos_y[i] = 0);

constraint let {array[1..field_h] of var int: lenghts = [count(field[j,..],1) | j in 1..field_h]} in longest_row = max(i in 1..field_h)(lenghts[i]);

constraint full_rows = sum([count(field[i,..], 1) div 10 == 1| i in 1..field_h]);

constraint unreachable = sum(
    [j - k+1 | i in 1..field_w, j in 1..field_h-1, k in 1..field_h-1 where j>=k /\ field[j+1,i]==1 /\ (field[k-1,i]==1 \/ k==1) /\ count(field[k..j, i], 0) == j-k+1]
);

solve :: seq_search([
    int_search(pos_x, first_fail, indomain_min),
    int_search(rotations, first_fail, indomain_min)])    
    maximize (priorities[1]*full_rows + priorities[2]*(field_h - h) + priorities[3]*longest_row + ((field_w*field_h) - unreachable));
    
output ["unreachable boxes = ", show(unreachable)]