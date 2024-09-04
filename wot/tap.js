import {createThing} from './blast.node.js';
import {StreamDeckMini, PhilipsHue} from './blast.tds.js';
import {HidHelpers} from './blast.hidHelpers.js';
import HID from 'node-hid';


async function gatStreamdeckquery(){
  HID.setDriverType('libusb');
  const devices = HID.devices();
  // delete devices without manufacturer and product
  const uniqueDevices = devices.filter(device => {
    return device.manufacturer && device.product;
  });

  return uniqueDevices[0]["path"]
}

globalThis.createThing = createThing
globalThis.StreamDeckMini = StreamDeckMini
globalThis.PhilipsHue = PhilipsHue
globalThis.HidHelpers = HidHelpers
globalThis.gatStreamdeckquery = gatStreamdeckquery
globalThis.HID = HID



//const args = process.argv.slice(2);

//const buttonNum = args[0];
// const hueMac = args[1]
// const hueOperation = args[2]


const buttonNum = 1;
const hueOperation = "writeProperty('power',0);"
const hueMac = "D4AA551E0F33"


const f = () => {
  console.log("Executing the code");
};


const codeToEval = `

const hueThing = await createThing(PhilipsHue, "${hueMac}");
const streamdeckPath = await gatStreamdeckquery();
console.log("Device connected. Input events will be logged here.")
console.log(streamdeckPath)

const streamdeckThing = await createThing(StreamDeckMini, streamdeckPath);
//console.log(streamdeckThing)
// Set the brightness to 100%

let status = await streamdeckThing.writeProperty('brightness', 100);
 
console.log(status);

console.log("Device connected! Input events will be logged here.")

// Array of booleans to track the state of each key
const keyState = new Array(6).fill(false)

const handleInputBuffer = async function (interactionOutput) {
  const data = await interactionOutput.value();
  // button events are reported as reportId 0x01
  if (data[0] === 1) {
    const keyData = data.slice(1, 7);
    for (let i = 0; i < 6; i++) {
      const keyPressed = Boolean(keyData[i]);
      const keyIndex = i;
      const stateChanged = keyPressed !== keyState[keyIndex];
      if (stateChanged) {
        keyState[keyIndex] = keyPressed;
        if (keyPressed) {
            if (keyIndex == ${buttonNum}){
                await hueThing.${hueOperation};  

            }else {
          await hueThing.writeProperty('power', 1);  

            }
        console.log('down', keyIndex);
        } else {
          console.log('up', keyIndex);
        }
      }
    }
  }
}

streamdeckThing.subscribeEvent('inputreport', handleInputBuffer);
`


const AsyncFunction = new Function(
  'return Object.getPrototypeOf(async function(){}).constructor'
)();
const func = new AsyncFunction(
  'f',
  `${codeToEval}
    f();`
);

await func(f);

//process.exit(0);

//"streamdeckThing.subscribeEvent('buttonPress', 0) => philipshue.writeProperty('power', 0);"