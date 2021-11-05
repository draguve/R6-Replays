
console.log(JSON.stringify(Process.enumerateModules(),null,4));

const ReadFile = Module.getExportByName(null, "ReadFile");

const MAXSIZE = 512;
var GetFinalPathNameByHandleA = new NativeFunction( Module.getExportByName(null, 'GetFinalPathNameByHandleA'), "uint32", ["pointer","pointer","uint32","uint32"]);

Interceptor.attach(ReadFile, {
  onEnter(args) {
    // console.log("--------------------------")
    // for(let x=0;x<10;x++){
    //   console.log(args[x]);
    // }
    
    var fileName = Memory.alloc(MAXSIZE);
    var size = GetFinalPathNameByHandleA(args[0],fileName,MAXSIZE,0);
    if(size){
      console.log(size);
      console.log(hexdump(fileName, { offset: 0,  length: size,  header: true, ansi: false}));
    }
    // console.log("ReadFile called from : \n" +
    //     Thread.backtrace(this.context, Backtracer.ACCURATE)
    //     .map(DebugSymbol.fromAddress).join('\n') + '\n');
  }
});

// frida -n RainbowSix.exe -l .\Frida\agent.js