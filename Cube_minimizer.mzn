include "globals.mzn";

int: cols;
int: rows;

array [1..rows, 1..cols] of int: field;

int: max_rect = sum(array1d(field));
array[1..max_rect] of var 0..cols: left_xs;
array[1..max_rect] of var 0..rows: left_ys;
array[1..max_rect] of var 0..cols: right_xs;
array[1..max_rect] of var 0..rows: right_ys;
array[1..max_rect] of var 0..rows*cols: areas;

%var 1..cols: left_x;
%var 1..rows: left_y;
%var 1..cols: right_x;
%var 1..rows: right_y;
%var 1..rows*cols: area;

constraint forall(i in 1..max_rect)(left_xs[i] <= right_xs[i] /\ left_ys[i] <= right_ys[i]);
constraint forall(i in 1..max_rect)(
    if left_ys[i] != 0 /\ right_ys[i] !=0 /\ left_xs[i] != 0 /\ right_xs[i] != 0
    then areas[i] = (right_xs[i] - left_xs[i] + 1)*(right_ys[i] - left_ys[i] + 1)
    else areas[i] = 0
    endif
);
    
constraint forall(rect in 1..max_rect)(
    if left_ys[rect] != 0 /\ right_ys[rect] !=0 /\ left_xs[rect] != 0 /\ right_xs[rect] != 0
    then sum(i in left_ys[rect]..right_ys[rect], j in left_xs[rect]..right_xs[rect])(
        field[i,j]
    ) == areas[rect]
    endif
);

constraint diffn(left_xs, left_ys, [right_xs[i] - left_xs[i] | i in 1..max_rect], [right_ys[i] - left_ys[i] | i in 1..max_rect]);

constraint sum(areas) == max_rect;

solve maximize count(areas, 0);

output [
    "left_xs = ", show(left_xs), "\n",
    "left_ys = ", show(left_ys), "\n",
    "right_xs = ", show(right_xs), "\n",
    "right_ys = ", show(right_ys), "\n",
    "areas = ", show(areas), "\n"
]

