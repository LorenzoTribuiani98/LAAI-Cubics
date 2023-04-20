include "globals.mzn";
include "diffn.mzn";

%---FUNCTIONS---%

%return the index of the last element in an array
function var int: find_last(array[int] of var int: x, var int: el)=
    max( [ if x[i] == el then i else 0 endif | i in index_set(x)]);
    


%---INPUTS---%
int: field_w = 10;                                 %width of the field
int: field_h = 20;                                 %height of the field 
int: n;                                            %number of already existing blocks
array[1..field_h, 1..field_w] of var 0..1: field;  %a binary matrix representing the field


set of int: blocks = 1..n;
set of int: new_blocks = 1..2;
array[blocks] of int: blocks_x;                    %x position of blocks 
array[blocks] of int: blocks_y;                    %y position of blocks 
array[blocks] of int: blocks_w;                    %blocks width 
array[blocks] of int: blocks_h;                    %blocks height



%---VARS---%
array[1..field_w] of var int: pos_y_full;          %relative y of blocks

array[new_blocks] of int: widths;                  %width of the blocks to place
array[new_blocks] of int: heights;                 %height of the blocks to place

array[new_blocks] of var bool: rotations;          %rotations array

%definition of width and hegiths according to the rotations vector
array[new_blocks] of var int: actual_widths = [(widths[i]*(1-rotations[i]) + heights[i]*rotations[i]) | i in new_blocks];
array[new_blocks] of var int: actual_heights = [(widths[i]*rotations[i]) + heights[i]*(1-rotations[i])| i in new_blocks];

var 0..field_h: full_rows;                         %number of completed rows
var 0..field_w: longest_row;                       %length of the longest consicutive row
var 0..field_w*field_h: unreachable;               %number of unreachable boxes
var 1..field_h: h;                                 %height

array[new_blocks] of var 0..field_w-1: pos_x;      %position x of the blocks to place
array[new_blocks] of var 0..field_h-1: pos_y;      %position y of the blocks to place

array[1..4] of int: priorities = [18,10,3,10];        %multiplicative weights



%---CONSTAINTS---%

% BOARD BOUNDARIES 
constraint max(i in new_blocks)(pos_x[i] + actual_widths[i]) <= field_w;   
constraint max(i in new_blocks)(pos_y[i] + actual_heights[i]) <= h;

% NON OVERLAPPING
constraint diffn(blocks_x++pos_x, blocks_y++pos_y, blocks_w++actual_widths, blocks_h++actual_heights);

% CUMULATIVE
constraint cumulative(blocks_y++pos_y, blocks_h++actual_heights, blocks_w++actual_widths, field_w);
constraint cumulative(blocks_x++pos_x, blocks_w++actual_widths, blocks_h++actual_heights, h);

%FIELD INITIALIZATION
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

%REALTIVE Y
constraint forall(i in new_blocks)(pos_y[i] = pos_y_full[pos_x[i] + 1] - actual_heights[i]);

% BLOCK ORDER
constraint (pos_x[2] in pos_x[1]..pos_x[1]+widths[1] \/ 
            pos_x[2]+widths[2] in pos_x[1]..pos_x[1]+widths[1]) ->
            pos_y[1] < pos_y[2];    
            
                                                            
% VARIABLE ASSIGNMENT
constraint pos_y_full = [find_last(field[..,i], 1)| i in 1..field_w];

constraint forall(i in new_blocks)(field[pos_y[i],pos_x[i]+1] = 1 \/ pos_y[i] = 0);

constraint let {array[1..field_h] of var int: lenghts = [count(field[j,..],1) | j in 1..field_h]} in longest_row = max(i in 1..field_h)(lenghts[i]);

constraint full_rows = sum([count(field[i,..], 1) div 10 == 1| i in 1..field_h]); %number of completed rows

constraint unreachable = sum(
    [j - k+1 | i in 1..field_w, j in 1..field_h-1, k in 1..field_h-1 where j>=k /\ field[j+1,i]==1 /\ (field[k-1,i]==1 \/ k==1) /\ count(field[k..j, i], 0) == j-k+1]
);
                                                

%---SEARCH STRATEGY---%
solve :: seq_search([
    int_search(pos_x, first_fail, indomain_min),
    int_search(rotations, first_fail, indomain_min)])    
    %maximize (priorities[1]*full_rows + priorities[2]*(field_h - h) + priorities[3]*longest_row + ((field_w*field_h) - unreachable));
    maximize (priorities[1]*full_rows + priorities[3]*longest_row - priorities[2]*h - priorities[4]*unreachable);