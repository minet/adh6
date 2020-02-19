    import { HttpUrlEncodingCodec } from '@angular/common/http';

/**
* CustomHttpUrlEncodingCodec
* Fix plus sign (+) not encoding, so sent as blank space
* See: https://github.com/angular/angular/issues/11058#issuecomment-247367318
*/
export class CustomHttpUrlEncodingCodec extends HttpUrlEncodingCodec {
    encodeKey(k: string): string {
        k = super.encodeKey(k);
        k = k.replace(/\+/gi, '%2B');
        k = k.replace('%5B', '[');
        k = k.replace('%5D', ']');
        return k;
    }
    encodeValue(v: string): string {
        v = super.encodeValue(v);
        return v.replace(/\+/gi, '%2B');
    }
}

