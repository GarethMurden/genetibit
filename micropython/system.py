import gc

def memory_in_use():
	gc.collect()
	free_bytes = gc.mem_free()
	used_bytes = gc.mem_alloc()
	total_bytes = free_bytes + used_bytes
	used_perc = (used_bytes / total_bytes) * 100
	return int(used_perc)