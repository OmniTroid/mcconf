import copy


# Modifies the given result dicts value given by tree_path to value
def modify_result_dict(result_dict: dict, tree_path: [str], value):
	key = tree_path[0]

	if len(tree_path) == 1:
		result_dict[key] = value
		return

	if key not in result_dict:
		result_dict[key] = {tree_path[1]: {}}

	modify_result_dict(result_dict[key], tree_path[1:], value)


def traverse(result_dict: dict, sub_dict: dict, tree_path: [str]):
	for key, value in sub_dict.items():
		new_tree_path = copy.deepcopy(tree_path)
		new_tree_path.append(key)
		# TODO: Somehow implement list merge here
		# if type(value) is list:
		#	 modify_result_dict(result_dict, new_tree_path, value)
		if type(value) is not dict:
			modify_result_dict(result_dict, new_tree_path, value)
		else:
			traverse(result_dict, sub_dict[key], new_tree_path)


# Combine a set of sub dicts into a result dict
def combine_dicts(dicts: [dict]):
	result_dict = {}

	for dict_ in dicts:
		traverse(result_dict, dict_, [])

	return result_dict


# Merge two dicts
def merge_dicts(dict_a: dict, dict_b: dict):
	result_dict = {}

	for key, value in dict_a.items():
		# If it's not in dict_b, just add it, no need for merge logic
		if key not in dict_b:
			result_dict[key] = value
			continue

	for key, value in dict_b.items():
		# If it's not in dict_a, just add it, no need for merge logic
		if key not in dict_a:
			result_dict[key] = value
			continue

	# At this point, the disjoint set of keys should be in result dict
	# So now, we need to deal with the intersection of keys, which all need to be either merged or overwritten
	# TODO: Implement merge logic

	return result_dict


def merge_lists(list_a: list, list_b: list):
	return list(set(list_a + list_b))
