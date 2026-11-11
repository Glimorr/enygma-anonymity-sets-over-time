package service

import (
    "encoding/csv"
    "encoding/json"
    "fmt"
    "math/big"
    mathrand "math/rand"
    "os"
    "path/filepath"
    "sort"
    "strconv"
    "strings"
    "testing"
)

// TestW2ObserverSelection invokes the pinned relayer's production
// getAnonymityIndex/fulfillAnonimitySet functions. The recipient schedule is
// synthetic and deterministic. Padding is the REAL crypto/rand implementation.
// These output files are NOT blockchain transactions.
func TestW2ObserverSelection(t *testing.T) {
    out := os.Getenv("ENYGMA_W2_OUTPUT")
    if out == "" {
        t.Skip("ENYGMA_W2_OUTPUT not set")
    }
    if err := os.MkdirAll(out, 0755); err != nil { t.Fatal(err) }
    publicPath := filepath.Join(out, "hub_observer_only.csv")
    truthPath := filepath.Join(out, "ground_truth_private.csv")
    publicFile, err := os.Create(publicPath)
    if err != nil { t.Fatal(err) }
    defer publicFile.Close()
    truthFile, err := os.Create(truthPath)
    if err != nil { t.Fatal(err) }
    defer truthFile.Close()
    pub := csv.NewWriter(publicFile)
    truth := csv.NewWriter(truthFile)
    defer pub.Flush()
    defer truth.Flush()
    if err := pub.Write([]string{"scenario", "sequence", "sender_chain", "anonymity_set"}); err != nil { t.Fatal(err) }
    if err := truth.Write([]string{"scenario", "sequence", "actual_receivers", "kind", "preferred_receiver"}); err != nil { t.Fatal(err) }

    type scenario struct {
        Name string `json:"scenario"`
        N int `json:"participants"`
        Count int `json:"observations"`
        Mode string `json:"traffic_model"`
        K int `json:"k"`
    }
    sc := []scenario{
        {"A_N6_balanced",6,500,"balanced",0},
        {"B_N7_preferred",7,500,"preferred60",0},
        {"C_N8_balanced",8,500,"balanced",0},
        {"D_N8_preferred",8,500,"preferred60",0},
        {"E_N8_positive",8,500,"preferred100",0},
        {"F_N8_mixedzero",8,500,"preferred60_zero25",0},
        {"G_N8_multireceiver",8,500,"preferred60_two",0},
        {"H_N10_preferred",10,500,"preferred60",0},
        {"I_N20_preferred",20,500,"preferred60",0},
        {"J_N8_zeroonly",8,500,"zeroonly",0},
    }
    // Seed is for the *synthetic recipient schedule only*.
    // The official relayer crypto/rand.Reader remains non-deterministic.
    rng := mathrand.New(mathrand.NewSource(20261111))
    for i := range sc {
        run := &sc[i]
        bankIDs := make([]*big.Int,run.N)
        for j := range bankIDs {
            bankIDs[j] = big.NewInt(int64(1001+j))
        }
        k,err:=getAnonymityIndex(run.N)
        if err!=nil {t.Fatal(err)}
        run.K=k
        preferred:=1002+rng.Intn(run.N-1)
        for j:=1;j<=run.Count;j++ {
            kind:="payment"
            receivers:=[]int{}
            receiver:=0
            if run.Mode=="zeroonly" || (run.Mode=="preferred60_zero25" && rng.Intn(4)==0) {
                kind="zero_only"
            } else {
                switch run.Mode {
                case "balanced":
                    receiver=1002+rng.Intn(run.N-1)
                case "preferred100":
                    receiver=preferred
                default:
                    if rng.Float64()<0.60 {
                        receiver=preferred
                    } else {
                        // Uniformly choose one of the other N-2 receivers.
                        skip:=rng.Intn(run.N-2)
                        for candidate:=1002;candidate<=1000+run.N;candidate++ {
                            if candidate==preferred {continue}
                            if skip==0 {receiver=candidate;break}
                            skip--
                        }
                    }
                }
                receivers=append(receivers,receiver)
                if run.Mode=="preferred60_two" {
                    kind="multi_receiver"
                    second:=1002+rng.Intn(run.N-2)
                    if second>=receiver {second++}
                    receivers=append(receivers,second)
                }
            }
            mandatory:=[]*big.Int{big.NewInt(1001)}
            for _,receiverID:=range receivers {
                mandatory=append(mandatory,big.NewInt(int64(receiverID)))
            }
            members,err:=fulfillAnonimitySet(k,mandatory,bankIDs)
            if err!=nil {t.Fatalf("%s iteration %d: %v",run.Name,j,err)}
            if len(members)!=k {t.Fatalf("wrong k for %s: %d",run.Name,len(members))}
            present:=map[int]bool{}
            memberIDs:=make([]int,len(members))
            for n,m:=range members {
                memberIDs[n]=int(m.Int64())
                if present[memberIDs[n]] {t.Fatalf("duplicate member")}
                present[memberIDs[n]]=true
            }
            for _,r:=range receivers {
                if !present[r] {t.Fatalf("true receiver absent")}
            }
            seq:=strconv.Itoa(j)
            ids:=make([]string,len(memberIDs))
            for n,id:=range memberIDs {ids[n]=strconv.Itoa(id)}
            if err:=pub.Write([]string{run.Name,seq,"1001",strings.Join(ids,"|")});err!=nil {t.Fatal(err)}
            rec:=make([]string,len(receivers))
            sort.Ints(receivers)
            for n,r:=range receivers{rec[n]=strconv.Itoa(r)}
            prefStr:=strconv.Itoa(preferred)
            if run.Mode=="balanced" || run.Mode=="zeroonly" {prefStr=""}
            if err:=truth.Write([]string{run.Name,seq,strings.Join(rec,"|"),kind,prefStr});err!=nil {t.Fatal(err)}
        }
    }
    pub.Flush()
    truth.Flush()
    if err:=pub.Error();err!=nil {t.Fatal(err)}
    if err:=truth.Error();err!=nil {t.Fatal(err)}
    b,err:=json.MarshalIndent(struct {
        EvidenceType string `json:"evidence_type"`
        SourceFunction string `json:"source_function"`
        TruthSeed int64 `json:"truth_seed"`
        Scenarios []scenario `json:"scenarios"`
    }{"NATIVE_SOURCE_FUNCTION_WITH_SYNTHETIC_TRAFFIC","fulfillAnonimitySet",20261111,sc},"","  ")
    if err!=nil {t.Fatal(err)}
    if err:=os.WriteFile(filepath.Join(out,"native_scenario_metadata.json"),append(b,'\n'),0644);err!=nil {t.Fatal(err)}
    fmt.Printf("W2_NATIVE_SELECTION_COMPLETE scenarios=%d observations=%d\n",len(sc),len(sc)*500)
}
