import 'package:get_storage/get_storage.dart';

class SLocalStorage {
  static final SLocalStorage _instance = SLocalStorage._internal();

  factory SLocalStorage() {
    return _instance;
  }

  SLocalStorage._internal();

  final _storage = GetStorage();

  // Generic method to save data
  Future<void> saveData<T>(String key, T value) async {
    await _storage.write(key, value);
  }

  // Generic method to read data
  T? readData<T>(String key) {
    return _storage.read<T>(key);
  }

  // Check if data exists
  bool containsKey(String key) {
    return _storage.hasData(key);
  }

  // Remove specific data
  Future<void> removeData(String key) async {
    await _storage.remove(key);
  }

  // Clear all data
  Future<void> clearAll() async {
    await _storage.erase();
  }

  // Save a list of data
  Future<void> saveList<T>(String key, List<T> value) async {
    await _storage.write(key, value);
  }

  // Read a list of data
  List<T>? readList<T>(String key) {
    return _storage.read<List<T>>(key);
  }

  // Add item to a list
  Future<void> addToList<T>(String key, T item) async {
    List<T>? currentList = readList<T>(key);
    currentList ??= [];
    currentList.add(item);
    await saveList(key, currentList);
  }

  // Remove item from a list by value
  Future<void> removeFromList<T>(String key, T item) async {
    List<T>? currentList = readList<T>(key);
    if (currentList != null) {
      currentList.remove(item);
      await saveList(key, currentList);
    }
  }

  // Clear a specific list
  Future<void> clearList(String key) async {
    await _storage.remove(key);
  }
}