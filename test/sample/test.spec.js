const $ = require('jquery');
const fs = require('fs');
const path = require('path');
const chai = require("chai");
const should = chai.should();
const JWebDriver = require('jwebdriver');
chai.use(JWebDriver.chaiSupportChainPromise);
const resemble = require('resemblejs-node');
resemble.outputSettings({
    errorType: 'flatDifferenceIntensity'
});

const rootPath = getRootPath();

module.exports = function(){

    let driver, testVars;

    before(function(){
        let self = this;
        driver = self.driver;
        testVars = self.testVars;
    });

    it('url: https://mtchoun-mouh.mongulu.cm/', async function(){
        await driver.url(_(`https://mtchoun-mouh.mongulu.cm/`));
    });

    it('waitBody: ', async function(){
        await driver.sleep(500).wait('body', 30000).html().then(function(code){
            isPageError(code).should.be.false;
        });
    });

    it('scrollTo: 0, 200', async function(){
        await driver.scrollTo(0, 200);
    });

    it('click: #name-input, 140, 33, 0', async function(){
        await driver.sleep(300).wait('#name-input', 30000)
               .sleep(300).mouseMove(140, 33).click(0);
    });

    it('sendKeys: MET', async function(){
        await driver.sendKeys('MET');
    });

    it('click: #email-input, 50, 6, 0', async function(){
        await driver.sleep(300).wait('#email-input', 30000)
               .sleep(300).mouseMove(50, 6).click(0);
    });

    it('sendKeys: met@gmail.com', async function(){
        await driver.sendKeys('met@gmail.com');
    });

    it('click: body, 720, 565, 0', async function(){
        await driver.sleep(300).wait('body', 30000)
               .sleep(300).mouseMove(720, 565).click(0);
    });

    it('scrollTo: 0, 268', async function(){
        await driver.scrollTo(0, 268);
    });

    it('click: Soumettre ( //button[text()="Soumettre"], 134, 26, 0 )', async function(){
        await driver.sleep(300).wait('//button[text()="Soumettre"]', 30000)
               .sleep(300).mouseMove(134, 26).click(0);
    });

    it('click: confirmationName ( #confirmationName, 158, 20, 0 )', async function(){
        await driver.sleep(300).wait('#confirmationName', 30000)
               .sleep(300).mouseMove(158, 20).click(0);
    });

    it('sendKeys: MET', async function(){
        await driver.sendKeys('MET');
    });

    it('click: confirmationEmail ( #confirmationEmail, 135, 14, 0 )', async function(){
        await driver.sleep(300).wait('#confirmationEmail', 30000)
               .sleep(300).mouseMove(135, 14).click(0);
    });

    it('sendKeys: met@gmail.com', async function(){
        await driver.sendKeys('met@gmail.com');
    });

    it('click: Confirm ( #confirmationModal button, 69, 8, 0 )', async function(){
        await driver.sleep(300).wait('#confirmationModal button', 30000)
               .sleep(300).mouseMove(69, 8).click(0);
    });

    it('click: #errorMessage p, 63, 11, 0', async function(){
        await driver.sleep(300).wait('#errorMessage p', 30000)
               .sleep(300).mouseMove(63, 11).click(0);
    });

    it('mouseDown: #errorMessage p, 2.79998779296875, 12.800003051757812, 0', async function(){
        await driver.sleep(300).wait('#errorMessage p', 30000)
               .sleep(300).mouseMove(2.79998779296875, 12.800003051757812).mouseDown(0);
    });

    it('mouseUp: #errorMessage p, 248, 36, 0', async function(){
        await driver.sleep(300).wait('#errorMessage p', 30000)
               .sleep(300).mouseMove(248, 36).mouseMove(248, 36).mouseUp(0);
    });

    it('click: #errorMessage p, 290, 33, 0', async function(){
        await driver.sleep(300).wait('#errorMessage p', 30000)
               .sleep(300).mouseMove(290, 33).click(0);
    });

    function _(str){
        if(typeof str === 'string'){
            return str.replace(/\{\{(.+?)\}\}/g, function(all, key){
                return testVars[key] || '';
            });
        }
        else{
            return str;
        }
    }

};

if(module.parent && /mocha\.js/.test(module.parent.id)){
    runThisSpec();
}

function runThisSpec(){
    // read config
    let webdriver = process.env['webdriver'] || '';
    let proxy = process.env['wdproxy'] || '';
    let config = require(rootPath + '/config.json');
    let webdriverConfig = Object.assign({},config.webdriver);
    let host = webdriverConfig.host;
    let port = webdriverConfig.port || 4444;
    let group = webdriverConfig.group || 'default';
    let match = webdriver.match(/([^\:]+)(?:\:(\d+))?/);
    if(match){
        host = match[1] || host;
        port = match[2] || port;
    }
    let testVars = config.vars;
    let browsers = webdriverConfig.browsers;
    browsers = browsers.replace(/^\s+|\s+$/g, '');
    delete webdriverConfig.host;
    delete webdriverConfig.port;
    delete webdriverConfig.group;
    delete webdriverConfig.browsers;

    // read hosts
    let hostsPath = rootPath + '/hosts';
    let hosts = '';
    if(fs.existsSync(hostsPath)){
        hosts = fs.readFileSync(hostsPath).toString();
    }
    let specName = path.relative(rootPath, __filename).replace(/\\/g,'/').replace(/\.js$/,'');

    browsers.split(/\s*,\s*/).forEach(function(browserName){
        let caseName = specName + ' : ' + browserName;

        let browserInfo = browserName.split(' ');
        browserName = browserInfo[0];
        let browserVersion = browserInfo[1];

        describe(caseName, function(){

            this.timeout(600000);
            this.slow(1000);

            let driver;
            before(function(){
                let self = this;
                let driver = new JWebDriver({
                    'host': host,
                    'port': port
                });
                let sessionConfig = Object.assign({}, webdriverConfig, {
                    'group': group,
                    'browserName': browserName,
                    'version': browserVersion,
                    'ie.ensureCleanSession': true,
                });
                if(proxy){
                    sessionConfig.proxy = {
                        'proxyType': 'manual',
                        'httpProxy': proxy,
                        'sslProxy': proxy
                    }
                }
                else if(hosts){
                    sessionConfig.hosts = hosts;
                }

                try {
                    self.driver = driver.session(sessionConfig).windowSize(1024, 768).config({
                        pageloadTimeout: 30000, // page onload timeout
                        scriptTimeout: 5000, // sync script timeout
                        asyncScriptTimeout: 10000 // async script timeout
                    });
                } catch (e) {
                    console.log(e);
                }

                self.testVars = testVars;
                let casePath = path.dirname(caseName);
                if (config.reporter && config.reporter.distDir) {
                    self.screenshotPath = config.reporter.distDir + '/reports/screenshots/' + casePath;
                    self.diffbasePath = config.reporter.distDir + '/reports/diffbase/' + casePath;
                } else {
                    self.screenshotPath = rootPath + '/reports/screenshots/' + casePath;
                    self.diffbasePath = rootPath + '/reports/diffbase/' + casePath;
                }
                self.caseName = caseName.replace(/.*\//g, '').replace(/\s*[:\.\:\-\s]\s*/g, '_');
                mkdirs(self.screenshotPath);
                mkdirs(self.diffbasePath);
                self.stepId = 0;
                return self.driver;
            });

            module.exports();

            beforeEach(function(){
                let self = this;
                self.stepId ++;
                if(self.skipAll){
                    self.skip();
                }
            });

            afterEach(async function(){
                let self = this;
                let currentTest = self.currentTest;
                let title = currentTest.title;
                if(currentTest.state === 'failed' && /^(url|waitBody|switchWindow|switchFrame):/.test(title)){
                    self.skipAll = true;
                }

                if ((config.screenshots && config.screenshots.captureAll && !/^(closeWindow):/.test(title)) || currentTest.state === 'failed') {
                    const casePath = path.dirname(caseName);
                    const filepath = `${self.screenshotPath}/${self.caseName}_${self.stepId}`;
                    const relativeFilePath = `./screenshots/${casePath}/${self.caseName}_${self.stepId}`;
                    let driver = self.driver;
                    try{
                        // catch error when get alert msg
                        await driver.getScreenshot(filepath + '.png');
                        let url = await driver.url();
                        let html = await driver.source();
                        html = '<!--url: '+url+' -->\n' + html;
                        fs.writeFileSync(filepath + '.html', html);
                        let cookies = await driver.cookies();
                        fs.writeFileSync(filepath + '.cookie', JSON.stringify(cookies));
                        appendToContext(self, relativeFilePath + '.png');
                    }
                    catch(e){}
                }
            });

            after(function(){
                return this.driver.close();
            });

        });
    });
}

function getRootPath(){
    let rootPath = path.resolve(__dirname);
    while(rootPath){
        if(fs.existsSync(rootPath + '/config.json')){
            break;
        }
        rootPath = rootPath.substring(0, rootPath.lastIndexOf(path.sep));
    }
    return rootPath;
}

function mkdirs(dirname){
    if(fs.existsSync(dirname)){
        return true;
    }else{
        if(mkdirs(path.dirname(dirname))){
            fs.mkdirSync(dirname);
            return true;
        }
    }
}

function callSpec(name){
    try{
        require(rootPath + '/' + name)();
    }
    catch(e){
        console.log(e)
        process.exit(1);
    }
}

function isPageError(code){
    return code == '' || / jscontent="errorCode" jstcache="\d+"|diagnoseConnectionAndRefresh|dnserror_unavailable_header|id="reportCertificateErrorRetry"|400 Bad Request|403 Forbidden|404 Not Found|500 Internal Server Error|502 Bad Gateway|503 Service Temporarily Unavailable|504 Gateway Time-out/i.test(code);
}

function appendToContext(mocha, content) {
    try {
        const test = mocha.currentTest || mocha.test;

        if (!test.context) {
            test.context = content;
        } else if (Array.isArray(test.context)) {
            test.context.push(content);
        } else {
            test.context = [test.context];
            test.context.push(content);
        }
    } catch (e) {
        console.log('error', e);
    }
};

function catchError(error){

}
