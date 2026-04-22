import java.io.*;

public class solution {

    static final int    INF  = 1 << 30;
    static final long   LINF = 1L << 62;
    static final int    MOD  = 1_000_000_007;
    static final double EPS  = 1e-9;
    static final double PI   = Math.acos(-1);
    static final String[] RET = {"NO", "YES"};

    // Pre-allocate arrays here with max sizes to reuse across test cases
    // static final int MAXN = ...;
    // static int[] arr = new int[MAXN];

    static StreamTokenizer in  = new StreamTokenizer(new BufferedReader(new InputStreamReader(System.in)));
    static PrintWriter      out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)));

    static int    nextInt()    throws IOException { in.nextToken(); return (int)  in.nval; }
    static long   nextLong()   throws IOException { in.nextToken(); return (long) in.nval; }
    static double nextDouble() throws IOException { in.nextToken(); return        in.nval; }
    static String nextString() throws IOException { in.nextToken(); return        in.sval; }

    static int  ceil   (int  n, int  m) { return (n + m - 1) / m; }
    static long addMod (long a, long b, long m) { return ((a % m) + (b % m))     % m; }
    static long subMod (long a, long b, long m) { return ((a % m) - (b % m) + m) % m; }
    static long mulMod (long a, long b, long m) { return ((a % m) * (b % m))     % m; }

    static void solve() throws IOException {

    }

    public static void main(String[] args) throws IOException {
        int testCases = 1;
        // testCases = nextInt();
        for (int tc = 1; tc <= testCases; tc++) {
            // out.print("Case #" + tc + ": ");
            solve();
        }
        out.flush();
    }
}
