import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:pointycastle/export.dart';

class EncryptionService {
  static const _saltLen = 16;
  static const _keyLen = 32;
  static const _iterations = 480000;
  static const _prefix = 'ENC:';

  Uint8List _pbkdf2(String password, Uint8List salt) {
    final deriv = PBKDF2KeyDerivator(HMac(SHA256Digest(), 32));
    deriv.init(Pbkdf2Parameters(salt, _iterations, _keyLen));
    return deriv.process(Uint8List.fromList(utf8.encode(password)));
  }

  Uint8List _aes128CbcEncrypt(Uint8List plaintext, Uint8List key, Uint8List iv) {
    final cipher = CBCBlockCipher(AESEngine())
      ..init(true, ParametersWithIV(KeyParameter(key), iv));
    final padded = _padPkcs7(plaintext, 16);
    final out = Uint8List(padded.length);
    var offset = 0;
    while (offset < padded.length) {
      offset += cipher.processBlock(padded, offset, out, offset);
    }
    return out;
  }

  Uint8List _aes128CbcDecrypt(Uint8List ciphertext, Uint8List key, Uint8List iv) {
    final cipher = CBCBlockCipher(AESEngine())
      ..init(false, ParametersWithIV(KeyParameter(key), iv));
    final out = Uint8List(ciphertext.length);
    var offset = 0;
    while (offset < ciphertext.length) {
      offset += cipher.processBlock(ciphertext, offset, out, offset);
    }
    return _unpadPkcs7(out);
  }

  Uint8List _padPkcs7(Uint8List data, int blockSize) {
    final padLen = blockSize - (data.length % blockSize);
    final padded = Uint8List(data.length + padLen)..setAll(0, data);
    for (var i = data.length; i < padded.length; i++) {
      padded[i] = padLen;
    }
    return padded;
  }

  Uint8List _unpadPkcs7(Uint8List data) {
    final padLen = data[data.length - 1];
    return data.sublist(0, data.length - padLen);
  }

  Uint8List _hmacSha256(Uint8List key, Uint8List data) {
    final hmac = HMac(SHA256Digest(), 64);
    hmac.init(KeyParameter(key));
    hmac.update(data, 0, data.length);
    final out = Uint8List(32);
    hmac.doFinal(out, 0);
    return out;
  }

  int _unixTimestamp() => (DateTime.now().millisecondsSinceEpoch / 1000).floor();

  Uint8List _int64ToBytes(int value) {
    final bytes = Uint8List(8);
    for (var i = 7; i >= 0; i--) {
      bytes[i] = value & 0xff;
      value >>= 8;
    }
    return bytes;
  }

  Uint8List _randomBytes(int length) {
    final rand = Random.secure();
    return Uint8List.fromList(List.generate(length, (_) => rand.nextInt(256)));
  }

  String encrypt(String plaintext, String password) {
    final salt = _randomBytes(_saltLen);
    final derivedKey = _pbkdf2(password, salt);

    final keyB64 = base64Url.encode(derivedKey);
    final fullKey = base64Url.decode(keyB64);
    final signingKey = fullKey.sublist(0, 16);
    final encKey = fullKey.sublist(16, 32);

    final iv = _randomBytes(16);
    final ciphertext = _aes128CbcEncrypt(Uint8List.fromList(utf8.encode(plaintext)), encKey, iv);

    final version = Uint8List.fromList([0x80]);
    final timestamp = _int64ToBytes(_unixTimestamp());

    final tokenPayload = Uint8List.fromList([...version, ...timestamp, ...iv, ...ciphertext]);
    final hmac = _hmacSha256(signingKey, tokenPayload);
    final token = Uint8List.fromList([...tokenPayload, ...hmac]);

    final combined = base64Url.encode(Uint8List.fromList([...salt, ...token]));
    return _prefix + combined;
  }

  String decrypt(String encryptedData, String password) {
    if (!encryptedData.startsWith(_prefix)) {
      throw FormatException('Not a protected QR code (missing ENC: prefix)');
    }

    final raw = base64Url.decode(encryptedData.substring(_prefix.length));
    final salt = raw.sublist(0, _saltLen);
    final tokenBytes = raw.sublist(_saltLen);

    final derivedKey = _pbkdf2(password, salt);
    final keyB64 = base64Url.encode(derivedKey);
    final fullKey = base64Url.decode(keyB64);
    final signingKey = fullKey.sublist(0, 16);
    final encKey = fullKey.sublist(16, 32);

    final version = tokenBytes[0];
    if (version != 0x80) {
      throw FormatException('Invalid token version: ${version.toRadixString(16)}');
    }

    final iv = tokenBytes.sublist(9, 25);
    final hmacLen = 32;
    final ciphertext = tokenBytes.sublist(25, tokenBytes.length - hmacLen);
    final expectedHmac = tokenBytes.sublist(tokenBytes.length - hmacLen);

    final payloadToVerify = tokenBytes.sublist(0, tokenBytes.length - hmacLen);
    final actualHmac = _hmacSha256(signingKey, payloadToVerify);

    if (!_equalBytes(expectedHmac, actualHmac)) {
      throw ArgumentError('Wrong password');
    }

    final decrypted = _aes128CbcDecrypt(ciphertext, encKey, iv);
    return utf8.decode(decrypted);
  }

  bool isEncrypted(String data) => data.startsWith(_prefix);

  bool _equalBytes(Uint8List a, Uint8List b) {
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}
