function var int: find_pos_y(array[int] of var int: x, var int: el)=
    max( [ if x[i] == el then i else 0 endif | i in index_set(x)]);
    
